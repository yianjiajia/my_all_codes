# -*- coding:utf8 -*-
__author__ = 'root'
import traceback
import logging
import copy
from oslo_config import cfg
from alarm.zabbixsync import zabbix_dbbase as dbbase
from openstack_client import OpenstackApi


'''
绑定告警策略对象时执行
1.绑定instance|router告警对象时，会传入object_id与strigger_id
    a.首先查找zabbix数据库ids表的table_name = trigger ,field_name = triggerid行的nextid值,插入新告警策略
    b.根据object_id,查找items表中name字段包含该字段的行 (#虚拟机与路由器已经被自动发现规则添加,items_discovery表中记录支持的监控项，
    资源无效的情况下，会重新发现，重新生成itemid)
    c.然后依据strigger_id,过滤sys_triggers_items行 #(('router_NET_I', '>', '80', '10'),
     ('router_NET_BW_O', '>', '100', '20')) #horizon端自定义添加
    d.根据horizon添加的sys_trigger_items,过滤b步骤中itemid
    e.将得到的itemid(一个或多个)与triggerid(相同的),和c步骤中得到的规则，插入到functions表中(functionid根据ids表查询)
    f.将得到的functionid与c步骤得到的比较字符串(>),组装成expression，如{12345} > 5 and {45678} > 6,插入到对应的trigger


2.添加内网与外网的ping, tcp , http/https触发器执行以下流程
    a.添加外网ping,tcp,http/https告警触发器时，页面根据用户填入的IP地址判断触发器类型
    b.提交时需要创建自定义items(根据sys_triggers_items),graph,trigger,graphs_items


#sys_trigger_items
将router_NET_I等换为对应的itemid
(('router_NET_I', '>', '80', '10'), ('router_NET_BW_O', '>', '100', '20'))
将itemid 与 triggerid ，持续时间，插入到functions表，生成的functionid和operator与value转化为expression，插入到对应的trigger行
#

#zabbix items
((23979L, 'qrouter-9965f790-edd2-44d3-861a-2dc7bc9f8ddd - Octets RX', 'netns-router.octets-rx[qrouter-9965f790-edd2-44d3-861a-2dc7bc9f8ddd]'),
 (23981L, 'qrouter-9965f790-edd2-44d3-861a-2dc7bc9f8ddd - Octets TX', 'netns-router.octets-tx[qrouter-9965f790-edd2-44d3-861a-2dc7bc9f8ddd]'),
 (23983L, 'qrouter-9965f790-edd2-44d3-861a-2dc7bc9f8ddd - Packets RX', 'netns-router.packets-rx[qrouter-9965f790-edd2-44d3-861a-2dc7bc9f8ddd]'),
 (23985L, 'qrouter-9965f790-edd2-44d3-861a-2dc7bc9f8ddd - Packets TX', 'netns-router.packets-tx[qrouter-9965f790-edd2-44d3-861a-2dc7bc9f8ddd]'))

netcheck_ping_internal,
netcheck_http_internal,
netcheck_tcp_internal,

netcheck_ping_external,
netcheck_http_external,
netcheck_tcp_external,
'''

ITEM_DICT = {
    'instance_DISK_R': 'collectd-libvirt.disk-oct-read',
    'instance_DISK_W': 'collectd-libvirt.disk-oct-write',
    'instance_DISK_OPS_R': 'collectd-libvirt.disk-ops-read',
    'instance_DISK_OPS_W': 'collectd-libvirt.disk-ops-write',
    'instance_NET_BW_I': 'collectd-libvirt.net-octets-rx',
    'instance_NET_BW_O': 'collectd-libvirt.net-octets-tx',
    'instance_NET_I': 'collectd-libvirt.net-packets-rx',
    'instance_NET_O': 'collectd-libvirt.net-packets-tx',
    'router_USE_RATE': ['netns-router.octets-rx', 'netns-router.octets-tx']
}

ITEM_DICT_UNIT = {
    'instance_DISK_R': 1024,
    'instance_DISK_W': 1024,
    'instance_DISK_OPS_R': 1,
    'instance_DISK_OPS_W': 1,
    'instance_NET_BW_I': 131072,
    'instance_NET_BW_O': 131072,
    'instance_NET_I': 1,
    'instance_NET_O': 1,
    'router_USE_RATE': 131072
}

NET_ITEM_DICT = {
    'inner-NET': {
        'Ping_State': 'netcheck_ping_internal',
        'Http/Https': 'netcheck_http_internal',
        'Tcp_State': 'netcheck_tcp_internal'
    },
    'outer-NET': {
        'Ping_State': 'netcheck_ping_external',
        'Http/Https': 'netcheck_http_external',
        'Tcp_State': 'netcheck_tcp_external'
    }
}

CONF = cfg.CONF
hostid = [
    cfg.IntOpt('out_net_agent_hostid', default=10115, help=''),
]
CONF.register_opts(hostid)


def mysql_query(mysql, sql):
    """数据库查询函数"""
    data = None
    res = mysql.query(sql, mode=dbbase.STORE_RESULT_MODE)
    res = mysql.fetch_queryresult(res, how=0, moreinfo=False)
    if res:
        data = res[0][0]
    return data


def mysql_mutil_query(mysql, sql):
    res = mysql.query(sql, mode=dbbase.STORE_RESULT_MODE)
    data = mysql.fetch_queryresult(res, how=0, moreinfo=False)
    return data


def get_router_region(mysql, object_id):
    """获取区域：通过graphid查找graphs_items表中对应的itemid,
    然后通过itemid查items表中对应的hostid,
    根据hostid查找hosts表中对应的主机名"""
    router_like = '%' + object_id + '%'
    sql = 'SELECT hosts.name FROM hosts WHERE hosts.hostid IN' \
          '(SELECT items.hostid FROM items WHERE items.name LIKE "%s")' % router_like
    # 调用query方法,得到result
    res = mysql.query(sql, mode=dbbase.STORE_RESULT_MODE)
    # 提取数据
    data = mysql.fetch_queryresult(res, how=0, moreinfo=False)
    region = ''
    if 'r1' in data[0][0]:
        region = 'RegionOne'
    if 'r2' in data[0][0]:
        region = 'RegionTwo'
    if 'r3' in data[0][0]:
        region = 'RegionThree'
    if 'r4' in data[0][0]:
        region = 'RegionFour'
    if 'r5' in data[0][0]:
        region = 'RegionFive'
    if 'r6' in data[0][0]:
        region = 'RegionSix'
    return region


# 创建内网与外网告警策略------>
def get_hostid(mysql, trigger_type, object_id):
    """获取内网检测router的hostid"""
    hostid = CONF.out_net_agent_hostid
    if trigger_type == 'inner-NET':
        router_object_id = object_id.split(',')[0]
        like_object = '%' + router_object_id.split('qrouter-')[1] + '%'
        get_router_hostid_sql = 'SELECT hostid FROM items WHERE name LIKE "%s"' % like_object
        hostid = mysql_query(mysql, get_router_hostid_sql)
    return hostid


def create_net_item_name_key(trigger_type, object_id, object_type, operator, value):
    name = 'openstack_net_monitor_item'
    if object_type == 'Ping_State':
        sub_str = ',' + value + ']'
    else:
        sub_str = ',' + operator + ',' + value + ']' if operator == 'contain' or operator == 'not_contain' else ']'
    _key = NET_ITEM_DICT[trigger_type][object_type] + '[' + object_id + sub_str
    return name, _key


def get_host_interfaceid(mysql, hostid):
    sql = "SELECT interfaceid FROM interface WHERE hostid=%d" % hostid
    interfaceid = mysql_query(mysql, sql)
    return interfaceid


def enable_net_item(mysql, itemid):
    sql = "UPDATE items SET status=0, error=NULL WHERE itemid=%s" % itemid
    mysql.execute(sql)
    mysql.commit()


def check_net_item(mysql, strigger_id, object_id, object_type, operator, value):
    nextid = None
    get_trigger_type_sql = "SELECT trigger_type FROM sys_triggers WHERE strigger_id='%s'" % strigger_id
    check_agent_item_sql = "SELECT itemid, hostid FROM items WHERE key_='%s'"
    # 查询触发器类型
    trigger_type = mysql_query(mysql, get_trigger_type_sql)
    hostid = get_hostid(mysql, trigger_type, object_id)
    # 获取主机interfaceid
    name, key_ = create_net_item_name_key(trigger_type, object_id, object_type, operator, value)
    # zabbix agent item是否重复校验
    data = mysql_mutil_query(mysql, check_agent_item_sql % key_)
    if data and data[0][1] == hostid:
        nextid = data[0][0]
        enable_net_item(mysql, data[0][0])
    return data and data[0][1] == hostid, nextid, hostid, name, key_


def create_net_item(mysql, strigger_id, object_id, object_name, object_type, operator, value):
    max_itemid_sql = "SELECT nextid FROM ids WHERE table_name='items' AND field_name='itemid'"
    create_item_sql = "INSERT INTO items(itemid, hostid, name, key_, delay, history, params, description, interfaceid)" \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    # 检查监控项
    same_item, nextid, hostid, name, key_ = check_net_item(mysql, strigger_id, object_id, object_type, operator, value)
    # 获取主机interfaceid
    interfaceid = get_host_interfaceid(mysql, hostid)
    # zabbix agent item是否重复校验
    if not same_item:
        nextid = mysql_query(mysql, max_itemid_sql) + 1
        args = (nextid, hostid, name, key_, 60, 14, '', '', interfaceid)
        mysql.execute(create_item_sql, args, mode=dbbase.DICTCURSOR_MODE)
        update_triggerid_sql = "UPDATE ids SET nextid=%d WHERE table_name='items' AND field_name='itemid'" % nextid
        # 创建zabbix graphs
        graphid = create_net_graph(mysql, object_name)
        create_net_graphs_items(mysql, graphid, nextid)
        mysql.execute(update_triggerid_sql)
        # 更新itemid最大值
        mysql.commit()
    return nextid, same_item


def create_net_graphs_items(mysql, graphid, itemid):
    gitemid = get_graphs_items_max_id(mysql)
    insert_net_graphs_items_sql = "INSERT INTO graphs_items(gitemid, graphid, itemid) VALUES (%s, %s, %s)"
    args = (gitemid, graphid, itemid)
    mysql.execute(insert_net_graphs_items_sql, args, mode=dbbase.DICTCURSOR_MODE)
    mysql.commit()


def create_net_graph(mysql, grpah_name):
    graphid = get_graph_max_id(mysql)
    insert_net_graph_sql = "INSERT INTO graphs(graphid, name) VALUES (%s, %s)"
    args = (graphid, grpah_name)
    mysql.execute(insert_net_graph_sql, args, mode=dbbase.DICTCURSOR_MODE)
    mysql.commit()
    return graphid


def get_graph_max_id(mysql):
    max_functionid_sql = "SELECT nextid FROM ids WHERE table_name='graphs' AND field_name='graphid'"
    graphid = mysql_query(mysql, max_functionid_sql) + 1
    update_triggerid_sql = "UPDATE ids SET nextid='%s' WHERE table_name='graphs' " \
                           "AND field_name='graphid'" % graphid
    mysql.execute(update_triggerid_sql)
    mysql.commit()
    return graphid


def get_graphs_items_max_id(mysql):
    max_functionid_sql = "SELECT nextid FROM ids WHERE table_name='graphs_items' AND field_name='gitemid'"
    gitemid = mysql_query(mysql, max_functionid_sql) + 1
    update_triggerid_sql = "UPDATE ids SET nextid='%s' WHERE table_name='graphs_items' " \
                           "AND field_name='gitemid'" % gitemid
    mysql.execute(update_triggerid_sql)
    mysql.commit()
    return gitemid


def get_function_max_id(mysql):
    max_functionid_sql = "SELECT nextid FROM ids WHERE table_name='functions' AND field_name='functionid'"
    functionid = mysql_query(mysql, max_functionid_sql) + 1
    update_triggerid_sql = "UPDATE ids SET nextid='%s' WHERE table_name='functions' " \
                           "AND field_name='functionid'" % functionid
    mysql.execute(update_triggerid_sql)
    mysql.commit()
    return functionid


def create_net_function(mysql, strigger_id, object_id, object_name, object_type, operator, value, keep_time):
    try:
        insert_function_sql = "INSERT INTO functions(functionid, itemid, triggerid, " \
                              "function, parameter) VALUES (%s, %s, %s, %s, %s)"
        keep_time = str(keep_time) + 's' if keep_time else 0
        functionid = get_function_max_id(mysql)
        triggerid = create_trigger(mysql, strigger_id)
        itemid, same_item = create_net_item(mysql, strigger_id, object_id, object_name, object_type, operator, value)
        function_name = 'avg' if object_type == 'Tcp_State' else 'last'
        args = [[functionid, itemid, triggerid, function_name, keep_time]]
        # functionid operation value
        mysql.execute(insert_function_sql, args, mode=dbbase.DICTCURSOR_MODE, many=True)
        mysql.commit()
        expression = '{' + str(functionid) + '}=1'
        return expression, triggerid
    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())


def update_net_function(mysql, strigger_id, object_id, object_name,
                        object_type, operator, value, keep_time, old_triggerid):
    try:
        insert_function_sql = "INSERT INTO functions(functionid, itemid, triggerid, " \
                              "function, parameter) VALUES (%s, %s, %s, %s, %s)"
        keep_time = str(keep_time) + 's' if keep_time else 0
        functionid = get_function_max_id(mysql)
        itemid, same_item = create_net_item(mysql, strigger_id, object_id, object_name, object_type, operator, value)
        if same_item:
            triggerid = old_triggerid
        else:
            triggerid = create_trigger(mysql, strigger_id)
        function_name = 'avg' if object_type == 'Tcp_State' else 'last'
        args = [[functionid, itemid, triggerid, function_name, keep_time]]
        # functionid operation value
        mysql.execute(insert_function_sql, args, mode=dbbase.DICTCURSOR_MODE, many=True)
        mysql.commit()
        expression = '{' + str(functionid) + '}=1'
        return expression, triggerid, same_item
    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())


# <------创建内网与外网告警策略


# 绑定与解绑instance与router------>
def create_trigger(mysql, strigger_id):
    max_triggerid_sql = "SELECT nextid FROM ids WHERE table_name='triggers' AND field_name='triggerid'"
    get_trigger_name_sql = "SELECT trigger_name FROM sys_triggers WHERE strigger_id='%s'" % strigger_id
    # 获取zabbix中triggers表最大ID
    create_trigger_sql = "INSERT INTO triggers(triggerid, description, comments, priority) VALUES (%s, %s, %s, %s)"
    nextid = mysql_query(mysql, max_triggerid_sql) + 1
    # 获取openstack自定义触发器名称
    trigger_name = mysql_query(mysql, get_trigger_name_sql)
    args = (nextid, trigger_name.encode('utf8'), 'openstack custom trigger', 3)
    update_triggerid_sql = "UPDATE ids SET nextid=%d WHERE table_name='triggers' AND field_name='triggerid'" % nextid
    mysql.execute(create_trigger_sql, args, mode=dbbase.DICTCURSOR_MODE)
    mysql.execute(update_triggerid_sql)
    mysql.commit()
    return nextid


def get_openstack_trigger_item(mysql, strigger_id):
    router_item = []
    trigger_item_sql = "SELECT item_name, operator, value, keep_time FROM " \
                       "sys_triggers_items WHERE strigger_id='%s'" % strigger_id
    data = mysql_mutil_query(mysql, trigger_item_sql)
    data = [list(i) for i in data]
    if data and data[0][0] == 'router_USE_RATE':
        for i in ITEM_DICT['router_USE_RATE']:
            sacle_list = copy.deepcopy(data[0][1:])
            sacle_list.insert(0, i)
            router_item.append(sacle_list)
        return router_item, ['router_USE_RATE', 'router_USE_RATE']
    return data, [i[0] for i in data]


def get_zabbix_items(mysql, object_id):
    like_object_id = '%' + object_id + '%'
    items_check_sql = "SELECT itemid, key_ FROM items WHERE name LIKE '%s'" % like_object_id
    data = mysql_mutil_query(mysql, items_check_sql)
    if not data:
        raise Exception('Template_Collectd_libvirt Discovery rules do not discover VM： ' + object_id)
    data = [list(i) for i in data]
    return data


def unit_conversion(mysql, item_type, object_id):
    unit_value = ITEM_DICT_UNIT[item_type]
    if item_type == 'router_USE_RATE':
        region = get_router_region(mysql, object_id)
        router_bandwidth = OpenstackApi().get_router_bandwidth(object_id, region_name=region)
        unit_value = router_bandwidth * ITEM_DICT_UNIT[item_type]
    return unit_value


def filter_items(mysql, strigger_id, object_id):
    openstack_trigger_items, item_type = get_openstack_trigger_item(mysql, strigger_id)
    scale = copy.copy(openstack_trigger_items)
    zabbix_trigger_items = get_zabbix_items(mysql, object_id)
    percentage = 0.01 if item_type == 'router_USE_RATE' else 1
    for i in openstack_trigger_items:
        item_key = i[0] if item_type[0] == 'router_USE_RATE' else ITEM_DICT[i[0]]
        unit_value = unit_conversion(mysql, item_type[openstack_trigger_items.index(i)], object_id)
        for j in zabbix_trigger_items:
            if item_key in j[1] and object_id in j[1]:
                scale[openstack_trigger_items.index(i)][0] = j[0]
                scale[openstack_trigger_items.index(i)][2] = str(
                    float(scale[openstack_trigger_items.index(i)][2]) * unit_value * percentage)
    return scale, item_type[0]


def filter_args(mysql, args):
    for i in args:
        max_functionid_sql = "SELECT nextid FROM ids WHERE table_name='functions' AND field_name='functionid'"
        functionid = mysql_query(mysql, max_functionid_sql) + 1
        update_triggerid_sql = "UPDATE ids SET nextid=%d WHERE table_name='functions' " \
                               "AND field_name='functionid'" % functionid
        mysql.execute(update_triggerid_sql)
        mysql.commit()
        i.insert(0, functionid)
    return args


def create_function(mysql, strigger_id, object_id):
    try:
        insert_function_sql = "INSERT INTO functions(functionid, itemid, triggerid, " \
                              "function, parameter) VALUES (%s, %s, %s, %s, %s)"
        triggerid = create_trigger(mysql, strigger_id)
        items, item_type = filter_items(mysql, strigger_id, object_id)
        a_args = [[i[0], triggerid, 'avg', i[3] + 'm'] for i in items]
        b_args = filter_args(mysql, a_args)
        # functionid operation value
        expression_args = ['{' + str(i[0]) + '}' + items[b_args.index(i)][1] + items[b_args.index(i)][2] for i in
                           b_args]
        join_str = ' or ' if item_type == 'router_USE_RATE' else ' and '
        expression = join_str.join(expression_args)
        mysql.execute(insert_function_sql, b_args, mode=dbbase.DICTCURSOR_MODE, many=True)
        mysql.commit()
        return expression, triggerid
    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())


def update_function(mysql, strigger_id, object_id, triggerid):
    try:
        insert_function_sql = "INSERT INTO functions(functionid, itemid, triggerid, " \
                              "function, parameter) VALUES (%s, %s, %s, %s, %s)"
        items, item_type = filter_items(mysql, strigger_id, object_id)
        a_args = [[i[0], triggerid, 'avg', i[3] + 'm'] for i in items]
        b_args = filter_args(mysql, a_args)
        # functionid operation value
        expression_args = ['{' + str(i[0]) + '}' + items[b_args.index(i)][1] + items[b_args.index(i)][2] for i in
                           b_args]
        join_str = ' or ' if item_type == 'router_USE_RATE' else ' and '
        expression = join_str.join(expression_args)
        mysql.execute(insert_function_sql, b_args, mode=dbbase.DICTCURSOR_MODE, many=True)
        mysql.commit()
        return expression, triggerid
    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())


def del_zabbix_functions(mysql, triggerids):
    sql = "DELETE FROM functions WHERE triggerid='%s'"
    mysql.execute(sql, triggerids, mode=dbbase.DICTCURSOR_MODE, many=True)
    mysql.commit()


def get_trigger_id_expression(mysql, strigger_id):
    triggerids_expressions = []
    sql = "SELECT object_id, trigger_id FROM sys_triggers_objects WHERE strigger_id='%s'" % strigger_id
    data = mysql_mutil_query(mysql, sql)
    if data:
        del_zabbix_functions(mysql, [i[1] for i in data])
        for i in data:
            function_res = update_function(mysql, strigger_id, i[0], i[1])
            triggerids_expressions.append(function_res)
    return triggerids_expressions


def create_zabbix_trigger(strigger_id, object_id, object_name, object_type, operator, value, keep_time,
                          operation_type=None):
    if operation_type == 'create_trigger':
        mysql = dbbase.PyMysql.get_instance()
        mysql.newConnection()
        get_trigger_type_sql = 'SELECT trigger_type FROM sys_triggers WHERE strigger_id="%s"' % strigger_id

        trigger_type = mysql_query(mysql, get_trigger_type_sql)
        if trigger_type in ['instance', 'router']:
            data = create_function(mysql, strigger_id, object_id)
        else:
            data = create_net_function(mysql, strigger_id, object_id, object_name, object_type, operator, value,
                                       keep_time)
        update_expression_sql = 'UPDATE triggers SET expression="%s" WHERE triggerid=%d' % data
        mysql.execute(update_expression_sql, mode=dbbase.DICTCURSOR_MODE)
        mysql.commit()
        mysql.closeConnnection()
        return data[1]


def del_zabbix_trigger(object_type, trigger_id, operation_type):
    mysql = dbbase.PyMysql.get_instance()
    mysql.newConnection()
    sql1 = 'DELETE FROM triggers WHERE triggerid=%d' % trigger_id
    sql3 = 'SELECT itemid FROM functions WHERE triggerid=%d' % trigger_id
    sql4 = "UPDATE items SET error='trigger is deleted with openstack user',status=1 WHERE itemid=%d"
    itemid = mysql_query(mysql, sql3)
    if object_type in ['instance', 'router']:
        mysql.execute(sql1, mode=dbbase.DICTCURSOR_MODE)
    if object_type in ['Ping_State', 'Http/Https', 'Tcp_State']:
        if operation_type == 'delete_trigger':
            mysql.execute(sql4 % itemid, mode=dbbase.DICTCURSOR_MODE)
    mysql.commit()
    mysql.closeConnnection()


def update_zabbix_trigger(strigger_id):
    get_trigger_type_sql = 'SELECT trigger_type FROM sys_triggers WHERE strigger_id="%s"' % strigger_id
    mysql = dbbase.PyMysql.get_instance()
    mysql.newConnection()
    trigger_type = mysql_query(mysql, get_trigger_type_sql)
    if trigger_type in ['instance', 'router']:
        sql = 'UPDATE triggers SET expression=%s WHERE triggerid="%s"'
        args = get_trigger_id_expression(mysql, strigger_id)
        mysql.execute(sql, args, mode=dbbase.DICTCURSOR_MODE, many=True)
        mysql.commit()
    mysql.closeConnnection()


def del_net_old_data(mysql, triggerid):
    if triggerid:
        sql1 = "SELECT itemid FROM functions WHERE triggerid=%d" % triggerid
        sql2 = "UPDATE items SET error='trigger is deleted with openstack user',status=1 WHERE itemid=%d"
        itemid = mysql_query(mysql, sql1)
        mysql.execute(sql2 % itemid, mode=dbbase.DICTCURSOR_MODE)
        mysql.commit()


def update_net_zabbix_trigger(strigger_id, object_id, object_name,
                              object_type, operator, value, keep_time):
    mysql = dbbase.PyMysql.get_instance()
    mysql.newConnection()
    sql1 = 'UPDATE triggers SET expression=%s WHERE triggerid=%s'
    sql2 = "UPDATE sys_triggers_objects SET trigger_id=%s WHERE strigger_id=%s"
    sql3 = "SELECT trigger_id FROM sys_triggers_objects WHERE strigger_id='%s'" % strigger_id
    triggerid = mysql_query(mysql, sql3)
    args = update_net_function(mysql, strigger_id, object_id, object_name,
                               object_type, operator, value, keep_time, triggerid)
    mysql.execute(sql2, (args[1], strigger_id), mode=dbbase.DICTCURSOR_MODE)
    mysql.execute(sql1, args[:2], mode=dbbase.DICTCURSOR_MODE)
    mysql.commit()
    if not args[2]:
        del_net_old_data(mysql, triggerid)
    mysql.closeConnnection()

# 绑定与解绑instance与router------>


