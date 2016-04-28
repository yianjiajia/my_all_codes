__author__ = 'gaga'
# -*- coding:utf-8 -*-
'''
@author: Gaga.Yan
'''
from alarm.db.operation.dboperation import SysAlarmLogsAction
from alarm.util.handlerUtil import *
from oslo_log import log as logging
from alarm.util.pagePackage import *


LOG = logging.getLogger(__name__)


def listByPage(conditionJson, likeConditionjson=None, page_no=1, page_size=15, headers=None, **kwargs):
    '''
    分页查询告警历史
    '''
    try:
        triggerlog = SysAlarmLogsAction()
        result = triggerlog.getalarmlogByPage(triggerlog.getQueryByCondition(conditionJson,
                                                                             likeConditionjson), page_no, page_size)
        dataResult = []
        if result:
            for i in result:
                dataResult.append(getJsonFromObj(i))
        return outSuccess("alarmlogList", pagePackage("alarmlogs", dataResult, page_no=result.no,
                                                      page_size=result.page_size, total=result.total))
    except Exception as e:
        LOG.error(str(e))
        return outError("取得告警历史列表失败！")


def get_count_problem(user_id):
    try:
        triggerlog = SysAlarmLogsAction()
        result = triggerlog.get_count_problem(user_id)
        return json.dumps(result, cls=CJsonEncoder, ensure_ascii=False)
    except Exception as e:
        LOG.error(str(e))
        return outError("取得告警历史列表失败！")



