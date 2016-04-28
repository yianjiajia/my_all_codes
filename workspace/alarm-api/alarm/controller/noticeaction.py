__author__ = 'gaga'
# -*- coding:utf-8 -*-
'''
Created on 2015-1-9

@author: yanjiajia
'''

from alarm.api import wsgi
from alarm.hander import notice_action
from alarm.util.controllerUtil import *
import json


class Controller(wsgi.Controller):
    """告警接收人接口处理"""
    def list(self, req, **args):
        page_no = req.params.get('pageNo')
        page_size = req.params.get('pageSize')
        page_no = int(page_no) if page_no else 1
        page_size = int(page_size) if page_size else 15
        conditionJson = getDictFromReq(req, inKeys=('user_id', 'type', 'region', 'status',
                                                    'pageNo', 'pageSize'))
        likeConditionjson = getDictFromReq(req, notInKeys=())
        return notice_action.listByPage(conditionJson, likeConditionjson, page_no, page_size)

    def create(self, req, **args):
        jsonParams = req.json_body
        return notice_action.add(jsonParams)

    def update(self, req, **args):
        notice_id = args.get('notice_id')
        jsonParams = req.json_body
        jsonParams['sys_notices']['notice_id'] = notice_id
        return notice_action.update(json.dumps(jsonParams))

    def delete(self, req, **args):
        notice_id = args.get('notice_id')
        return notice_action.delete(notice_id)

    def detail(self, req, **args):
        notice_id = args.get('notice_id')
        return notice_action.detail(notice_id)



def create_resource():
    return wsgi.Resource(Controller())