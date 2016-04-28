__author__ = 'gaga'
# -*- coding:utf-8 -*-
'''

@author: Gaga.Yan
'''
from alarm.db.operation.dboperation import SysNoticesAction
from alarm.db.object.models import SysNotices
from alarm.util.handlerUtil import *
from oslo_log import log as logging
from alarm.util.pagePackage import *


LOG = logging.getLogger(__name__)


def add(noticeJson, headers=None, **kwargs):
    """生成告警策略"""
    try:
        if isinstance(noticeJson, str):
            noticeJson = json.loads(noticeJson)
        noticeDict = noticeJson['sys_notices']
        notice = SysNotices()
        getObjFromJson(notice, noticeDict)
        noticeAdd = SysNoticesAction(notice)
        noticeAdd.add()
        return outSuccess("notices", getJsonFromObj(noticeAdd.sysNotices))
    except Exception as e:
        LOG.error(str(e))
        return outError("生成告警接收人失败！")


def update(noticeJson, headers=None, **kwargs):
    """更新告警策略"""
    try:
        if isinstance(noticeJson, str):
            noticeJson = json.loads(noticeJson)
        noticeDict = noticeJson['sys_notices']
        notice = SysNotices()
        notice.notice_id = noticeDict['notice_id']
        noticeOP = SysNoticesAction(notice)
        noticeOP.update(noticeDict)
        return outSuccess("notices", getJsonFromObj(noticeOP.sysNotices))
    except Exception as e:
        LOG.error(str(e))
        return outError("更新告警接收人失败！")


def listByPage(conditionJson, likeConditionjson=None, page_no=1, page_size=15, headers=None, **kwargs):
    '''
    分页查询策略
    '''
    try:
        notices = SysNoticesAction()
        result = notices.getNoticeByPage(notices.getQueryByCondition(conditionJson, likeConditionjson), page_no,
                                         page_size)
        dataResult = []
        if result:
            for i in result:
                dataResult.append(getJsonFromObj(i))
        return outSuccess("noticeList", pagePackage("notices", dataResult, page_no=result.no,
                                                    page_size=result.page_size, total=result.total))
    except Exception as e:
        LOG.error(str(e))
        return outError("取得接收人失败！")


def detail(notice_id):
    '''账号详情'''
    try:
        notice = SysNotices()
        notice.notice_id = notice_id
        noticeDao = SysNoticesAction(notice)
        noticeDao.detail()
        return outSuccess("notices", getJsonFromObj(noticeDao.sysNotices))
    except Exception as e:
        LOG.error(str(e))
        return outError("获取接收人详情失败！")


def getNoticeByUserID(user_id, conditionJson, likeConditionjson=None, page_no=1,
                      page_size=15, headers=None, **kwargs):
    '''根据user的ID查找告警策略'''
    try:
        conditionJson = json.loads(conditionJson)
        likeConditionjson = json.loads(likeConditionjson)
        noticeOP = SysNoticesAction()
        result = noticeOP.getNoticeByPage()(noticeOP.getQueryByCondition(conditionJson, likeConditionjson),
                                            page_no, page_size)
        noticeOP.getNoticeByPage(user_id)
        dataResult = []
        if result:
            for i in result:
                dataResult.append(getJsonFromObj(i))
        return outSuccess("noticeList", pagePackage("notices", dataResult, page_no=result.no,
                                                    page_size=result.page_size, total=result.total))
    except Exception as e:
        LOG.error(str(e))
        return outError("取得告警接收人失败！")


def delete(notice_id):
    try:
        notice = SysNotices()
        notice.notice_id = notice_id
        noticeOP = SysNoticesAction(notice)
        noticeOP.delete()
        return outSuccess("msg", "删除告警接收人成功！")
    except Exception as e:
        LOG.error(str(e))
        return outError("删除告警接收人失败！")


