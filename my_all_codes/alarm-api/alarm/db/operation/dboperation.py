# -*- coding:utf-8 -*-
'''
Created on 2015-8-21

@author: Gaga.Yan
云监控数据库操作类
'''
from alarm.db.sqlalchemy import session as sa
from alarm.db.object.models import (SysNotices, SysTriggers,
                                    SysTriggersObjects, SysTriggerItems,
                                    SysAlarmLogs)
from alarm.db.Pagination import Pagination
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class SysTriggersAction(object):
    def __init__(self, SysTriggers=None):
        self.SysTriggers = SysTriggers

    def getQuery(self, session=None):
        if not session:
            session = sa.get_session()
        return session.query(SysTriggers)

    def getQueryByCondition(self, condition=None, likeCondition=None, session=None):
        '''条件查询'''
        if not session:
            session = sa.get_session()
        if condition is None and likeCondition is None:
            return session.query(SysTriggers)
        query = session.query(SysTriggers)
        if condition:
            for (attr, attrValue) in [(key, value) for (key, value) in condition.items()]:
                if attr == 'user_id':
                    query = query.filter(SysTriggers.user_id == attrValue)
                if attr == 'trigger_main_type':
                    if attrValue == 'network':
                        query = query.filter(SysTriggers.trigger_type != 'router')
                        query = query.filter(SysTriggers.trigger_type != 'instance')
                    if attrValue == 'resource':
                        query = query.filter(SysTriggers.trigger_type != 'inner-NET')
                        query = query.filter(SysTriggers.trigger_type != 'outer-NET')
                if attr == 'trigger_type':
                    query = query.filter(SysTriggers.trigger_type == attrValue)
        return query.order_by('sys_triggers.created_at DESC')

    def list(self, condition=None, likeCondition=None, session=None):
        '''按条件查询所有的告警策略'''
        if not session:
            session = sa.get_session()
        query = self.getQueryByCondition(condition, likeCondition)
        rows = query.all()
        session.close()
        return rows

    def getAlarmByPage(self, query=None, page_no=1, page_size=15, edge_size=0, session=None):
        ''' 分页查询'''
        if not session:
            session = sa.get_session()
        if query is None:
            query = self.getQuery(session)
        pagination = Pagination(query)
        return pagination.paginate(page_no, page_size, edge_size)

    def add(self, session=None):
        '''添加策略'''
        try:
            if not session:
                session = sa.get_session()
            session.add(self.SysTriggers)
            session.flush()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def update(self, values, session=None):
        """数据更新"""
        try:
            if not session:
                session = sa.get_session()
            session.begin()
            self.SysTriggers = session.query(SysTriggers).filter(SysTriggers.strigger_id ==
                                                                 self.SysTriggers.strigger_id).first()
            self.SysTriggers.update(values)
            session.commit()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def detail(self, session=None):
        '''策略详情'''
        try:
            if not session:
                session = sa.get_session()
            self.SysTriggers = session.query(SysTriggers).filter(SysTriggers.strigger_id
                                                                 == self.SysTriggers.strigger_id).first()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def delete(self, session=None):
        try:
            if not session:
                session = sa.get_session()
            session.begin()
            self.SysTriggers = session.query(SysTriggers).filter(SysTriggers.strigger_id
                                                                 == self.SysTriggers.strigger_id).first()
            session.delete(self.SysTriggers)
            session.commit()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def getTriggerByUserID(self, user_id, session=None):
        '''根据user的ID查找账号'''
        try:
            if not session:
                session = sa.get_session()
            self.SysTriggers = session.query(SysTriggers).filter(SysTriggers.user_id == user_id).first()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e


class TriggerObjAction(object):
    def __init__(self, TriggerOBJ=None):
        self.TriggerOBJ = TriggerOBJ

    def getQuery(self, session=None):
        if not session:
            session = sa.get_session()
        return session.query(SysTriggersObjects)

    def getQueryByCondition(self, condition=None, likeCondition=None, session=None):
        '''条件查询'''
        if not session:
            session = sa.get_session()
        if condition is None and likeCondition is None:
            return session.query(SysTriggersObjects)
        query = session.query(SysTriggersObjects)
        if condition:
            for (attr, attrValue) in [(key, value) for (key, value) in condition.items()]:
                if attr == 'strigger_id':
                    query = query.filter(SysTriggersObjects.strigger_id == attrValue)
        return query.order_by('sys_triggers_objects.object_name')

    def list(self, condition=None, likeCondition=None, session=None):
        '''按条件查询所有的告警对象'''
        if not session:
            session = sa.get_session()
        query = self.getQueryByCondition(condition, likeCondition)
        rows = query.all()
        session.close()
        return rows

    def getTriggerObjByPage(self, query=None, page_no=1, page_size=15, edge_size=0, session=None):
        ''' 分页查询'''
        if not session:
            session = sa.get_session()
        if query is None:
            query = self.getQuery(session)
        pagination = Pagination(query)
        return pagination.paginate(page_no, page_size, edge_size)

    def add(self, session=None):
        '''添加策略'''
        try:
            if not session:
                session = sa.get_session()
            session.add(self.TriggerOBJ)
            session.flush()
            session.close()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def detail(self, session=None):
        '''策略详情'''
        try:
            if not session:
                session = sa.get_session()
            self.TriggerOBJ = session.query(SysTriggersObjects).filter(SysTriggersObjects.trigger_object_id
                                                                       == self.TriggerOBJ.trigger_object_id).first()
            return self.TriggerOBJ
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def delete(self, session=None):
        try:
            if not session:
                session = sa.get_session()
            session.begin()
            self.TriggerOBJ = session.query(SysTriggersObjects).filter(SysTriggersObjects.trigger_object_id
                                                                       == self.TriggerOBJ.trigger_object_id).first()
            session.delete(self.TriggerOBJ)
            session.commit()
            session.close()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def getByTriggerID(self, strigger_id, session=None):
        '''根据strigger的ID查找账号'''
        try:
            if not session:
                session = sa.get_session()
            query = session.query(SysTriggersObjects).filter(SysTriggersObjects.strigger_id == strigger_id)
            rows = query.all()
            session.close()
            return rows
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e


class SysNoticesAction(object):
    def __init__(self, sysNotices=None):
        self.sysNotices = sysNotices

    def getQuery(self, session=None):
        if not session:
            session = sa.get_session()
        return session.query(SysNotices)

    def getQueryByCondition(self, condition=None, likeCondition=None, session=None):
        '''条件查询'''
        if not session:
            session = sa.get_session()
        if condition is None and likeCondition is None:
            return session.query(SysNotices)
        query = session.query(SysNotices)
        if condition:
            for (attr, attrValue) in [(key, value) for (key, value) in condition.items()]:
                if attr == 'user_id':
                    query = query.filter(SysNotices.user_id == attrValue)
        return query.order_by('sys_notices.created_at DESC')

    def list(self, condition=None, likeCondition=None, session=None):
        '''按条件查询所有的告警策略'''
        if not session:
            session = sa.get_session()
        query = self.getQueryByCondition(condition, likeCondition)
        rows = query.all()
        session.close()
        return rows

    def getNoticeByPage(self, query=None, page_no=1, page_size=15, edge_size=0, session=None):
        ''' 分页查询'''
        if not session:
            session = sa.get_session()
        if query is None:
            query = self.getQuery(session)
        pagination = Pagination(query)
        return pagination.paginate(page_no, page_size, edge_size)

    def add(self, session=None):
        '''添加策略'''
        try:
            if not session:
                session = sa.get_session()
            session.add(self.sysNotices)
            session.flush()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e


    def update(self, values, session=None):
        """数据更新"""
        try:
            if not session:
                session = sa.get_session()
            session.begin()
            self.sysNotices = session.query(SysNotices).filter(SysNotices.notice_id ==
                                                               self.sysNotices.notice_id).first()
            self.sysNotices.update(values)
            session.commit()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def detail(self, session=None):
        '''策略详情'''
        try:
            if not session:
                session = sa.get_session()
            self.sysNotices = session.query(SysNotices).filter(SysNotices.notice_id ==
                                                               self.sysNotices.notice_id).first()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def delete(self, session=None):
        try:
            if not session:
                session = sa.get_session()
            session.begin()
            self.sysNotices = session.query(SysNotices).filter(SysNotices.notice_id ==
                                                               self.sysNotices.notice_id).first()
            session.delete(self.sysNotices)
            session.commit()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def getTriggerByUserID(self, user_id, session=None):
        '''根据user的ID查'''
        try:
            if not session:
                session = sa.get_session()
            query = session.query(SysNotices).filter(SysNotices.user_id == user_id)
            rows = query.all()
            session.close()
            return rows
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e


class SysTriggerItemsAction(object):
    def __init__(self, sysTriggerItems=None):
        self.sysTriggerItems = sysTriggerItems

    def getQuery(self, session=None):
        if not session:
            session = sa.get_session()
        return session.query(SysTriggerItems)

    def add(self, session=None):
        '''添加策略'''
        try:
            if not session:
                session = sa.get_session()
            session.add(self.sysTriggerItems)
            session.flush()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def update(self, values, session=None):
        """数据更新"""
        try:
            if not session:
                session = sa.get_session()
            session.begin()
            self.sysTriggerItems = session.query(SysTriggerItems).filter(SysTriggerItems.sys_trigger_item_id ==
                                                                         self.sysTriggerItems.sys_trigger_item_id).first()
            self.sysTriggerItems.update(values)
            session.commit()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def delete(self, session=None):
        try:
            if not session:
                session = sa.get_session()
            session.begin()
            self.sysTriggerItems = session.query(SysTriggerItems).filter(SysTriggerItems.sys_trigger_item_id ==
                                                                         self.sysTriggerItems.sys_trigger_item_id).first()
            session.delete(self.sysTriggerItems)
            session.commit()
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e

    def getByTriggerID(self, strigger_id, session=None):
        '''根据strigger的ID查找账号'''
        try:
            if not session:
                session = sa.get_session()
            query = session.query(SysTriggerItems).filter(SysTriggerItems.strigger_id == strigger_id)
            rows = query.all()
            session.close()
            return rows
        except Exception as e:
            session.close()
            LOG.error(str(e))
            raise e


class SysAlarmLogsAction(object):
    def __init__(self, sysAlarmLogs=None):
        self.sysAlarmLogs = sysAlarmLogs

    def getQuery(self, session=None):
        if not session:
            session = sa.get_session()
        return session.query(SysAlarmLogs)

    def getQueryByCondition(self, condition=None, likeCondition=None, session=None):
        '''条件查询'''
        if not session:
            session = sa.get_session()
        if condition is None and likeCondition is None:
            return session.query(SysAlarmLogs)
        query = session.query(SysAlarmLogs)
        if condition:
            for (attr, attrValue) in [(key, value) for (key, value) in condition.items()]:
                if attr == 'user_id':
                    query = query.filter(SysAlarmLogs.user_id == attrValue)
                if attr == 'alarm_object_name':
                    query = query.filter(SysAlarmLogs.alarm_object_name == attrValue)
                if attr == 'trigger_name':
                    query = query.filter(SysAlarmLogs.trigger_name == attrValue)
                if attr == 'alarm_content':
                    query = query.filter(SysAlarmLogs.alarm_content == attrValue)
                if attr == 'alarm_status':
                    query = query.filter(SysAlarmLogs.alarm_status == attrValue)
                if attr == 'trigger_type':
                    query = query.filter(SysAlarmLogs.trigger_type == attrValue)
                if attr == 'ended_at':
                    query = query.filter(SysAlarmLogs.ended_at == attrValue)
        return query.order_by('sys_alarm_logs.occurred_at DESC')

    def list(self, condition=None, likeCondition=None, session=None):
        '''按条件查询所有的告警历史'''
        if not session:
            session = sa.get_session()
        query = self.getQueryByCondition(condition, likeCondition)
        rows = query.all()
        session.close()
        return rows

    def getalarmlogByPage(self, query=None, page_no=1, page_size=15, edge_size=0, session=None):
        ''' 分页查询'''
        if not session:
            session = sa.get_session()
        if query is None:
            query = self.getQuery(session)
        pagination = Pagination(query)
        return pagination.paginate(page_no, page_size, edge_size)

    def get_count_problem(self, user_id, session=None):
        if not session:
            session = sa.get_session()
        query = session.query(SysAlarmLogs).filter(SysAlarmLogs.user_id == user_id)
        count = query.count()
        problem_count = query.filter(SysAlarmLogs.alarm_status == "PROBLEM").count()
        return {"count": count, "problem_count": problem_count}
