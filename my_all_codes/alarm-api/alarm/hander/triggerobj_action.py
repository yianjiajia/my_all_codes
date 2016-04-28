__author__ = 'gaga'
# -*- coding:utf-8 -*-
'''

@author: Gaga.Yan
'''
from alarm.db.operation.dboperation import TriggerObjAction
from alarm.db.object.models import SysTriggersObjects
from alarm.util.handlerUtil import *
from oslo_log import log as logging
from alarm.util.pagePackage import *
from alarm.zabbixsync import zabbix_dbsync

LOG = logging.getLogger(__name__)


def add(triggerobjJson, headers=None, **kwargs):
    """生成告警策略"""
    try:
        if isinstance(triggerobjJson, str):
            triggerobjJson = json.loads(triggerobjJson)
        triggerobjDict = triggerobjJson['sys_triggers_objects']

        # 同步zabbix数据库
        # 将zabbix生成的triggerid返回
        trigger_id = zabbix_dbsync.create_zabbix_trigger(triggerobjDict['strigger_id'],
                                                         triggerobjDict['object_id'],
                                                         triggerobjDict['object_name'],
                                                         triggerobjDict['object_type'],
                                                         triggerobjDict['operator'],
                                                         triggerobjDict['value'],
                                                         triggerobjDict['keep_time'],
                                                         triggerobjDict['operation_type'])
        triggerobjDict['trigger_id'] = trigger_id
        triggerobj = SysTriggersObjects()
        getObjFromJson(triggerobj, triggerobjDict)
        triggerObjAdd = TriggerObjAction(triggerobj)
        triggerObjAdd.add()
        return outSuccess("triggerObjs", getJsonFromObj(triggerObjAdd.TriggerOBJ))
    except Exception as e:
        LOG.error(str(e))
        return outError("关联告警对象失败！")


def listByPage(conditionJson, likeConditionjson=None, page_no=1, page_size=15, headers=None, **kwargs):
    '''
    分页查询策略
    '''
    try:
        triggerObj = TriggerObjAction()
        result = triggerObj.getTriggerObjByPage(triggerObj.getQueryByCondition(conditionJson, likeConditionjson),
                                                page_no, page_size)
        dataResult = []
        if result:
            for i in result:
                dataResult.append(getJsonFromObj(i))
        return outSuccess("triggerObjList", pagePackage("triggerObjs", dataResult, page_no=result.no,
                                                        page_size=result.page_size, total=result.total))
    except Exception as e:
        LOG.error(str(e))
        return outError("取得策略对象失败！")


def getByTriggerID(strigger_id, conditionJson, likeConditionjson=None, page_no=1,
                   page_size=15, headers=None, **kwargs):
    '''根据user的ID查找告警策略'''
    try:
        conditionJson = json.loads(conditionJson)
        likeConditionjson = json.loads(likeConditionjson)
        triggerObjOP = TriggerObjAction()
        result = triggerObjOP.getTriggerObjByPage(triggerObjOP.getQueryByCondition(conditionJson, likeConditionjson),
                                                  page_no, page_size)
        triggerObjOP.getByTriggerID(strigger_id)
        dataResult = []
        if result:
            for i in result:
                dataResult.append(getJsonFromObj(i))
        return outSuccess("triggerObjList", pagePackage("triggerObjs", dataResult, page_no=result.no,
                                                        page_size=result.page_size, total=result.total))
    except Exception as e:
        LOG.error(str(e))
        return outError("取得告警策略对象失败！")


def delete(trigger_object_id, operation_type):
    try:
        triggerObj = SysTriggersObjects()
        triggerObj.trigger_object_id = trigger_object_id
        triggerobjOP = TriggerObjAction(triggerObj)
        # 同步zabbix数据库triggers表，将对应的triggerid行删除
        object_type = triggerobjOP.detail().object_type
        trigger_id = triggerobjOP.detail().trigger_id
        strigger_id = triggerobjOP.detail().strigger_id
        triggerobjOP.delete()
        zabbix_dbsync.del_zabbix_trigger(object_type, trigger_id, operation_type)
        return outSuccess("msg", "删除告警策略对象成功！")
    except Exception as e:
        LOG.error(str(e))
        return outError("删除告警策略对象失败！")


