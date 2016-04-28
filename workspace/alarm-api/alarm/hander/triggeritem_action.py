__author__ = 'gaga'
# -*- coding:utf-8 -*-
'''

@author: Gaga.Yan
'''
from alarm.db.operation.dboperation import SysTriggerItemsAction
from alarm.db.object.models import SysTriggerItems
from alarm.util.handlerUtil import *
from oslo_log import log as logging
from alarm.util.pagePackage import *
from alarm.zabbixsync import zabbix_dbsync

LOG = logging.getLogger(__name__)


def add(triggeritemJson, headers=None, **kwargs):
    """生成触发器项"""
    try:
        if isinstance(triggeritemJson, str):
            triggeritemJson = json.loads(triggeritemJson)
        triggeritemDict = triggeritemJson['sys_triggers_items']
        triggeritem = SysTriggerItems()
        getObjFromJson(triggeritem, triggeritemDict)
        triggeritemAdd = SysTriggerItemsAction(triggeritem)
        triggeritemAdd.add()
        return outSuccess("triitems", getJsonFromObj(triggeritemAdd.sysTriggerItems))
    except Exception as e:
        LOG.error(str(e))
        return outError("生成触发器项失败！")


def update(triggeritemJson, headers=None, **kwargs):
    """更新告警策略"""
    try:
        if isinstance(triggeritemJson, str):
            triggeritemJson = json.loads(triggeritemJson)
        triggeritemDict = triggeritemJson['sys_triggers_items']
        triggeritem = SysTriggerItems()
        triggeritem.sys_trigger_item_id = triggeritemDict['sys_trigger_item_id']
        triggeritemOP = SysTriggerItemsAction(triggeritem)
        triggeritemOP.update(triggeritemDict)
        # 更新zabbix的triggers表
        zabbix_dbsync.update_net_zabbix_trigger(triggeritemDict['strigger_id'],
                                                triggeritemDict['object_id'],
                                                triggeritemDict['object_name'],
                                                triggeritemDict['object_type'],
                                                triggeritemDict['operator'],
                                                triggeritemDict['value'],
                                                triggeritemDict['keep_time'])
        return outSuccess("triitems", getJsonFromObj(triggeritemOP.sysTriggerItems))
    except Exception as e:
        LOG.error(str(e))
        return outError("更新触发器项失败！")


def getByTriggerID(strigger_id, headers=None, **kwargs):
    '''根据strigger_id查找触发器项'''
    try:
        triggeritemOP = SysTriggerItemsAction(SysTriggerItems)
        result = triggeritemOP.getByTriggerID(strigger_id)
        dataResult = []
        if result:
            for i in result:
                dataResult.append(getJsonFromObj(i))
        return outSuccess("triitemList", pagePackage('triitems', dataResult))

    except Exception as e:
        LOG.error(str(e))
        return outError("取得触发器项失败！")


def delete(sys_trigger_item_id):
    try:
        triggeritem = SysTriggerItems()
        triggeritem.sys_trigger_item_id = sys_trigger_item_id
        triggeritemOP = SysTriggerItemsAction(triggeritem)
        triggeritemOP.delete()
        return outSuccess("msg", "删除触发器项成功！")
    except Exception as e:
        LOG.error(str(e))
        return outError("删除触发器项失败！")


