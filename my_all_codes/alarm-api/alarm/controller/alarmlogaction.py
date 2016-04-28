__author__ = 'gaga'
# -*- coding:utf-8 -*-
'''
Created on 2015-1-14

@author: yanjiajia
'''

from alarm.api import wsgi
from alarm.hander import alarmlog_action
from alarm.util.controllerUtil import *


class Controller(wsgi.Controller):
    """告警接收人接口处理"""

    def list(self, req, **args):
        page_no = req.params.get('pageNo')
        page_size = req.params.get('pageSize')
        page_no = int(page_no) if page_no else 1
        page_size = int(page_size) if page_size else 15
        conditionJson = getDictFromReq(req, inKeys=('user_id', 'alarm_object_name', 'trigger_name', 'alarm_content',
                                                    'alarm_status', 'pageNo', 'pageSize', 'trigger_type',
                                                    'ended_at'))
        likeConditionjson = getDictFromReq(req, notInKeys=())
        return alarmlog_action.listByPage(conditionJson, likeConditionjson, page_no, page_size)

    def get_count_problem(self, req, **kargs):
        user_id = req.params.get('user_id')
        return alarmlog_action.get_count_problem(user_id)


def create_resource():
    return wsgi.Resource(Controller())