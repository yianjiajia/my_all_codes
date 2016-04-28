# -*- coding:utf-8 -*-
'''
Created on 2015-8-24

@author: yanjiajia
'''

from alarm.api import wsgi
from alarm.hander import trigger_action
from alarm.util.controllerUtil import *
import json
import datetime


class Controller(wsgi.Controller):
    """告警策略接口处理"""
    def list(self, req, **args):
        page_no = req.params.get('pageNo')
        page_size = req.params.get('pageSize')
        page_no = int(page_no) if page_no else 1
        page_size = int(page_size) if page_size else 15
        conditionJson = getDictFromReq(req, inKeys=('user_id', 'trigger_type', 'trigger_main_type',
                                                    'pageNo', 'pageSize'))
        likeConditionjson = getDictFromReq(req, notInKeys=())
        return trigger_action.listByPage(conditionJson, likeConditionjson, page_no, page_size)
    
    def create(self, req, **args):
        jsonParams = req.json_body
        return trigger_action.add(jsonParams)

    def update(self, req, **args):
        strigger_id = args.get('strigger_id')
        jsonParams = req.json_body
        jsonParams['sys_triggers']['strigger_id'] = strigger_id
        return trigger_action.update(json.dumps(jsonParams))

    def delete(self, req, **args):
        strigger_id = args.get('strigger_id')
        return trigger_action.delete(strigger_id)

    def detail(self, req, **args):
        strigger_id = args.get('strigger_id')
        return trigger_action.detail(strigger_id)

    def getTriggerByUserID(self, req, **args):
        page_no = req.params.get('pageNo')
        page_size = req.params.get('pageSize')
        page_no = int(page_no) if page_no else 1
        page_size = int(page_size) if page_size else 15
        conditionJson = getDictFromReq(req, inKeys=('trigger_type', 'pageNo', 'pageSize'))
        user_id = args.get('user_id')
        return trigger_action.getTriggerByUserID(user_id, json.dumps(conditionJson), page_no, page_size)


def create_resource():
    return wsgi.Resource(Controller())
