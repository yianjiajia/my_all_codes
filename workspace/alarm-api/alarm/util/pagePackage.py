# -*- coding:utf-8 -*-
'''
Created on 2014-7-14

@author: baoguodong.kevin
'''

""" page封装  """
def pagePackage(key, data, **kwargs):
    pageResult = {key: data}
    if kwargs is not None:
        if kwargs.has_key('page_no'):
            pageResult['page_no'] = kwargs['page_no']
        if kwargs.has_key('page_size'):
            pageResult['page_size'] = kwargs['page_size']
        if kwargs.has_key('total'):
            pageResult['total'] = kwargs['total']
        if kwargs.has_key('count'):
            pageResult['count'] = kwargs['count']
        if kwargs.has_key('start'):
            pageResult['start'] = kwargs['start']
    return pageResult