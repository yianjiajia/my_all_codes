# -*- coding:utf-8 -*-
'''

@author: Gaga.Yan
'''
from alarm.db.operation.dboperation import SysTriggersAction
from alarm.db.object.models import SysTriggers
from alarm.util.handlerUtil import *
from oslo_log import log as logging
from alarm.util.pagePackage import *
from alarm.zabbixsync import zabbix_dbsync

LOG = logging.getLogger(__name__)


def add(triggerJson, headers=None, **kwargs):
    """生成告警策略"""
    try:
        if isinstance(triggerJson, str):
            triggerJson = json.loads(triggerJson)
        triggerDict = triggerJson['sys_triggers']
        trigger = SysTriggers()
        getObjFromJson(trigger, triggerDict)
        triggerAdd = SysTriggersAction(trigger)
        triggerAdd.add()
        return outSuccess("triggers", getJsonFromObj(triggerAdd.SysTriggers))
    except Exception as e:
        LOG.error(str(e))
        return outError("生成告警策略失败！")


def update(triggerJson, headers=None, **kwargs):
    """更新告警策略"""
    try:
        if isinstance(triggerJson, str):
            triggerJson = json.loads(triggerJson)
        triggerDict = triggerJson['sys_triggers']
        trigger = SysTriggers()
        trigger.strigger_id = triggerDict['strigger_id']
        triggerOP = SysTriggersAction(trigger)
        triggerOP.update(triggerDict)
        # 更新zabbix的triggers表
        zabbix_dbsync.update_zabbix_trigger(triggerDict['strigger_id'])
        return outSuccess("triggers", getJsonFromObj(triggerOP.SysTriggers))
    except Exception as e:
        LOG.error(str(e))
        return outError("更新告警策略失败！")


def listByPage(conditionJson, likeConditionjson=None, page_no=1, page_size=15, headers=None, **kwargs):
    '''
    分页查询策略
    '''
    try:
        trigger = SysTriggersAction()
        result = trigger.getAlarmByPage(trigger.getQueryByCondition(conditionJson, likeConditionjson), page_no,
                                        page_size)
        dataResult = []
        if result:
            for i in result:
                dataResult.append(getJsonFromObj(i))
        return outSuccess("triggerList", pagePackage("triggers", dataResult, page_no=result.no,
                                                     page_size=result.page_size, total=result.total))
    except Exception as e:
        LOG.error(str(e))
        return outError("取得策略列表失败！")


def detail(strigger_id):
    '''账号详情'''
    try:
        trigger = SysTriggers()
        trigger.strigger_id = strigger_id
        triggerDao = SysTriggersAction(trigger)
        triggerDao.detail()
        return outSuccess("triggers", getJsonFromObj(triggerDao.SysTriggers))
    except Exception as e:
        LOG.error(str(e))
        return outError("取得告警策略详情失败！")


def getTriggerByUserID(user_id, conditionJson, likeConditionjson=None, page_no=1,
                       page_size=15, headers=None, **kwargs):
    '''根据user的ID查找告警策略'''
    try:
        conditionJson = json.loads(conditionJson)
        likeConditionjson = json.loads(likeConditionjson)
        triggerOP = SysTriggersAction()
        result = triggerOP.getAlarmByPage(triggerOP.getQueryByCondition(conditionJson, likeConditionjson),
                                          page_no, page_size)
        triggerOP.getTriggerByUserID(user_id)
        dataResult = []
        if result:
            for i in result:
                dataResult.append(getJsonFromObj(i))
        return outSuccess("triggerList", pagePackage("triggers", dataResult, page_no=result.no,
                                                     page_size=result.page_size, total=result.total))
    except Exception as e:
        LOG.error(str(e))
        return outError("取得告警策略失败！")


def delete(strigger_id):
    try:
        trigger = SysTriggers()
        trigger.strigger_id = strigger_id
        triggerOP = SysTriggersAction(trigger)
        triggerOP.delete()
        return outSuccess("msg", "删除告警策略成功！")
    except Exception as e:
        LOG.error(str(e))
        return outError("删除告警策略失败！")


