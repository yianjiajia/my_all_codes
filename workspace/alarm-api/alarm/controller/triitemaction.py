__author__ = 'gaga'
# -*- coding:utf-8 -*-
'''
Created on 2016-1-14

@author: yanjiajia
'''

from alarm.api import wsgi
from alarm.hander import triggeritem_action
from alarm.util.controllerUtil import *
import json
import datetime



class Controller(wsgi.Controller):
    """告警对象接口处理"""

    def update(self, req, **args):
        sys_trigger_item_id = int(args.get('sys_trigger_item_id'))
        jsonParams = req.json_body
        jsonParams['sys_triggers_items']['sys_trigger_item_id'] = sys_trigger_item_id
        return triggeritem_action.update(json.dumps(jsonParams))

    def create(self, req, **args):
        jsonParams = req.json_body
        return triggeritem_action.add(jsonParams)

    def delete(self, req, **args):
        sys_trigger_item_id = args.get('sys_trigger_item_id')
        return triggeritem_action.delete(sys_trigger_item_id)


    def getBytriggerID(self, req, **args):
        strigger_id= args.get('strigger_id')
        return triggeritem_action.getByTriggerID(strigger_id)


def create_resource():
    return wsgi.Resource(Controller())
