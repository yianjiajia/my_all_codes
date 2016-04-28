# -*- coding:utf-8 -*-


def getDictFromReq(req,inKeys=None,notInKeys=None):
    if inKeys:
        return {key: value for (key, value) in req.params.items() if key in inKeys}
    if notInKeys:
        return {key: value for (key, value) in req.params.items() if key not in inKeys}
    return {key: value for (key, value) in req.params.items()}