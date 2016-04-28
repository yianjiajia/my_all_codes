# -*- coding:utf-8 -*-
'''
Created on 2015-8-24

@author: baoguodong.kevin
'''
import json
from datetime import datetime
from datetime import date
from decimal import Decimal


class CJsonEncoder(json.JSONEncoder):    
    def default(self, obj):        
        if isinstance(obj, datetime):            
            return obj.strftime('%Y-%m-%d %H:%M:%S')        
        elif isinstance(obj, date):            
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj,Decimal):
            return str(obj)       
        else:
            try:            
                return json.JSONEncoder.default(self, obj)
            except Exception as e:
                d = {} 
#                print type(obj)
                d.update(obj.__dict__)
                return {key:d[key] for key in d.keys() if not key.startswith('_') }


""" 成功返回结果 """


def outSuccess(key, data):
    return json.dumps({key: data, "success": "success"}, cls=CJsonEncoder, ensure_ascii=False)

""" 错误返回结果 """


def outError(data):
    return json.dumps({"msg": data, "success": "error"}, ensure_ascii=False)

"""将JSON字典赋值给对象 """


def getObjFromJson(obj, jsonDict):
    if jsonDict:
        for (key, value) in jsonDict.items():
            if hasattr(obj, key):
                obj[key] = value

"""将对象转化为json的字典"""


def getJsonFromObj(obj, notInDict = []):
    if obj:
        jsonstr = {}
        for key in [x for x in dir(obj) if not x.startswith('_') and x not in ["get", "iteritems", "metadata", "next", "save", "update"] and x not in notInDict]:
            jsonstr[key] = getattr(obj, key)
        return jsonstr
    return None


if __name__ == "__main__":
    pass