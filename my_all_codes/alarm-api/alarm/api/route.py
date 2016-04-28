# -*- coding:utf-8 -*-
'''
Created on 2015-10-30

@author: gaga
'''

"""
WSGI middleware
"""

from oslo_config import cfg
from oslo_log import log as logging
import routes
import six
import stevedore
import webob.dec
import webob.exc
from alarm.api import wsgi
from alarm import wsgi as base_wsgi
from alarm.controller import triggeraction
from alarm.controller import triobjaction
from alarm.controller import noticeaction
from alarm.controller import triitemaction
from alarm.controller import alarmlogaction


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class APIMapper(routes.Mapper):
    def routematch(self, url=None, environ=None):
        if url == "":
            result = self._match("", environ)
            return result[0], result[1]
        return routes.Mapper.routematch(self, url, environ)

    def connect(self, *args, **kargs):
        # NOTE(vish): Default the format part of a route to only accept json
        #             and xml so it doesn't eat all characters after a '.'
        #             in the url.
        kargs.setdefault('requirements', {})
        if not kargs['requirements'].get('format'):
            kargs['requirements']['format'] = 'json|xml'
        return routes.Mapper.connect(self, *args, **kargs)


class ProjectMapper(APIMapper):
    def resource(self, member_name, collection_name, **kwargs):
        if 'parent_resource' not in kwargs:
            kwargs['path_prefix'] = '{project_id}/'
        else:
            parent_resource = kwargs['parent_resource']
            p_collection = parent_resource['collection_name']
            p_member = parent_resource['member_name']
            kwargs['path_prefix'] = '{project_id}/%s/:%s_id' % (p_collection,
                                                                p_member)
        routes.Mapper.resource(self, member_name,
                               collection_name, **kwargs)


class BaseRouter(base_wsgi.Router):
    """Routes requests on the OpenStack API to the appropriate controller
    and method.
    """
    ExtensionManager = None  # override in subclasses

    @classmethod
    def factory(cls, global_config, **local_config):
        """Simple paste factory, :class:`alarm.wsgi.Router` doesn't have one."""
        return cls()

    def __init__(self, ext_mgr=None, init_only=None):

        mapper = APIMapper()
        self.resources = {}
        self._setup_routes(mapper)
        super(BaseRouter, self).__init__(mapper)

    def _setup_routes(self, mapper):
        raise NotImplementedError()


class APIRouter(BaseRouter):
    """Routes requests on the OpenStack API to the appropriate controller
    and method.
    """
    def _setup_routes(self, mapper):
        '''
        url映射：
        1. sys_triggers：告警策略URL路由

        '''
        self.resources['sys_triggers'] = triggeraction.create_resource()
        mapper.connect("/alarm/trigger/create",
                       controller=self.resources['sys_triggers'],
                       action="create",
                       conditions={"method": ['POST']})

        mapper.connect("/alarm/trigger/detail/{strigger_id}",
                       controller=self.resources['sys_triggers'],
                       action="detail",
                       conditions={"method": ['GET']})

        mapper.connect("/alarm/trigger/update/{strigger_id}",
                       controller=self.resources['sys_triggers'],
                       action="update",
                       conditions={"method": ['PUT']})

        mapper.connect("/alarm/trigger/delete/{strigger_id}",
                       controller=self.resources['sys_triggers'],
                       action="delete",
                       conditions={"method": ['DELETE']})


        mapper.connect("/alarm/trigger/index",
                       controller=self.resources['sys_triggers'],
                       action="list",
                       conditions={"method": ['GET']})


        '''
        url映射：
        2. sys_triggers_objects：告警策略对象URL路由

        '''

        self.resources['sys_triggers_objects'] = triobjaction.create_resource()

        mapper.connect("/alarm/triggerobj/index",
                       controller=self.resources['sys_triggers_objects'],
                       action="list",
                       conditions={"method": ['GET']})

        mapper.connect("/alarm/triggerobj/create",
                       controller=self.resources['sys_triggers_objects'],
                       action="create",
                       conditions={"method": ['POST']})

        mapper.connect("/alarm/triggerobj/delete/{trigger_object_id}",
                       controller=self.resources['sys_triggers_objects'],
                       action="delete",
                       conditions={"method": ['DELETE']})


        '''
        url映射：
        3. sys_notices：告警接收人URL路由

        '''
        
        self.resources['sys_notices'] = noticeaction.create_resource()

        mapper.connect("/alarm/notice/index",
                       controller=self.resources['sys_notices'],
                       action="list",
                       conditions={"method": ['GET']})

        mapper.connect("/alarm/notice/detail/{notice_id}",
                       controller=self.resources['sys_notices'],
                       action="detail",
                       conditions={"method": ['GET']})

        mapper.connect("/alarm/notice/create",
                       controller=self.resources['sys_notices'],
                       action="create",
                       conditions={"method": ['POST']})

        mapper.connect("/alarm/notice/delete/{notice_id}",
                       controller=self.resources['sys_notices'],
                       action="delete",
                       conditions={"method": ['DELETE']})

        mapper.connect("/alarm/notice/update/{notice_id}",
                       controller=self.resources['sys_notices'],
                       action="update",
                       conditions={"method": ['PUT']})

        '''
        url映射：
        4. sys_triggers_items：触发器项URL路由

        '''
        self.resources['sys_triggers_items'] = triitemaction.create_resource()


        mapper.connect("/alarm/triggeritem/getBytriggerID/{strigger_id}",
                       controller=self.resources['sys_triggers_items'],
                       action="getBytriggerID",
                       conditions={"method": ['GET']})

        mapper.connect("/alarm/triggeritem/create",
                       controller=self.resources['sys_triggers_items'],
                       action="create",
                       conditions={"method": ['POST']})

        mapper.connect("/alarm/triggeritem/update/{sys_trigger_item_id}",
                       controller=self.resources['sys_triggers_items'],
                       action="update",
                       conditions={"method": ['PUT']})

        mapper.connect("/alarm/triggeritem/delete/{sys_trigger_item_id}",
                       controller=self.resources['sys_triggers_items'],
                       action="delete",
                       conditions={"method": ['DELETE']})


        '''
        url映射：
        5. sys_triggers_logs：告警历史URL路由

        '''
        self.resources['sys_alarm_logs'] = alarmlogaction.create_resource()


        mapper.connect("/alarm/alarmlog/index",
                       controller=self.resources['sys_alarm_logs'],
                       action="list",
                       conditions={"method": ['GET']})

        mapper.connect("/alarm/alarmlog/get_count_problem",
                       controller=self.resources['sys_alarm_logs'],
                       action="get_count_problem",
                       conditions={"method": ['GET']})
