# -*- coding:utf-8 -*-
from sqlalchemy import Column, Index, Integer, BigInteger, Enum, String, schema
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float, Numeric, DECIMAL
from sqlalchemy.orm import relationship, backref, object_mapper
from oslo_config import cfg
from alarm.db.sqlalchemy import models


CONF = cfg.CONF
BASE = declarative_base()


def MediumText():
    return Text().with_variant(MEDIUMTEXT(), 'mysql')


def init_db():
    BASE.metadata.create_all()


class AlarmBase(models.ModelBase):
    metadata = None


'''
云监控ORM
'''


class SysItems(BASE, AlarmBase, models.TimestampMixin):
    __tablename__ = 'sys_items'
    __table_args__ = ()
    sys_item_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(String(64), nullable=False)
    item_id = Column(BigInteger, nullable=False)


class SysGraphs(BASE, AlarmBase, models.TimestampMixin):
    __tablename__ = 'sys_graphs'
    __table_args__ = ()
    sys_graph_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(String(64), nullable=False)
    graph_id = Column(BigInteger, nullable=False)
    region = Column(String(10), nullable=False)
    graph_type = Column(String(20), nullable=False)


class SysNotices(BASE, AlarmBase, models.TimestampMixin):
    __tablename__ = 'sys_notices'
    __table_args__ = ()
    notice_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(String(64), nullable=False)
    mobile_number = Column(String(16), nullable=True)
    email = Column(String(64), nullable=True)
    comment = Column(MEDIUMTEXT, nullable=True)


class SysTriggers(BASE, AlarmBase, models.TimestampMixin):
    __tablename__ = 'sys_triggers'
    __table_args__ = ()
    strigger_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(String(64), nullable=False)
    trigger_name = Column(String(255), nullable=False, default='')
    trigger_type = Column(String(64), nullable=False)
    mobile = Column(String(10), nullable=True)
    email = Column(String(10), nullable=True)


class SysTriggersObjects(BASE, AlarmBase):
    __tablename__ = 'sys_triggers_objects'
    __table_args__ = ()
    trigger_object_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    strigger_id = Column(Integer, ForeignKey('sys_triggers.strigger_id'), nullable=False)
    object_id = Column(String(64), nullable=False)
    object_type = Column(String(16), nullable=False)
    object_name = Column(String(128), nullable=False, default='')
    trigger_id = Column(BigInteger, nullable=True)


class SysAlarmLogs(BASE, AlarmBase):
    __tablename__ = 'sys_alarm_logs'
    __table_args__ = ()
    sys_trigger_log_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(String(64), nullable=False)
    alarm_object_name = Column(String(64), nullable=False)
    alarm_content = Column(MEDIUMTEXT, nullable=False)
    alarm_status = Column(String(16), nullable=False)
    trigger_name = Column(String(64), nullable=False)
    trigger_type = Column(String(16), nullable=False)
    occurred_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=False)
    event_id = Column(BigInteger, nullable=False)


class SysTriggerItems(BASE, AlarmBase):
    __tablename__ = 'sys_triggers_items'
    __table_args__ = ()
    sys_trigger_item_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    strigger_id = Column(Integer, ForeignKey('sys_triggers.strigger_id'), nullable=False)
    item_name = Column(String(64), nullable=False)
    operator = Column(String(16), nullable=False)
    value = Column(String(64), nullable=False)
    keep_time = Column(String(10), nullable=False)






