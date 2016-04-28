__author__ = 'gaga'
# -*- coding:utf-8 -*-
'''
Created on 2016-1-8

@author: yanjiajia
'''

from alarm.api import wsgi
from alarm.hander import triggerobj_action
from alarm.util.controllerUtil import *
import json
import datetime



class Controller(wsgi.Controller):
    """告警对象接口处理"""
    def list(self, req, **args):
        page_no = req.params.get('pageNo')
        page_size = req.params.get('pageSize')
        page_no = int(page_no) if page_no else 1
        page_size = int(page_size) if page_size else 15
        conditionJson = getDictFromReq(req, inKeys=('strigger_id',
                                                    'pageNo', 'pageSize'))
        likeConditionjson = getDictFromReq(req, notInKeys=())
        return triggerobj_action.listByPage(conditionJson, likeConditionjson, page_no, page_size)

    def create(self, req, **args):
        jsonParams = req.json_body
        return triggerobj_action.add(jsonParams)

    def delete(self, req, **args):
        strigger_id = args.get('trigger_object_id')
        operation_type = req.params.get('operation_type')
        return triggerobj_action.delete(strigger_id, operation_type)


    def getBytriggerID(self, req, **args):
        page_no = req.params.get('pageNo')
        page_size = req.params.get('pageSize')
        page_no = int(page_no) if page_no else 1
        page_size = int(page_size) if page_size else 15
        conditionJson = getDictFromReq(req, inKeys=('type', 'region', 'status'))
        strigger_id = args.get('strigger_id')
        return triggerobj_action.getByTriggerID(strigger_id, json.dumps(conditionJson), page_no, page_size)


def create_resource():
    return wsgi.Resource(Controller())
