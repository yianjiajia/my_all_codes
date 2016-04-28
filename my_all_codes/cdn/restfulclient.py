__author__ = 'gaga'

import urllib2
import urllib
from django.conf import settings
import json

BASE_URL = "http://192.168.100.50:6891/v1.0/naas"


class RequestClient(object):
    def __init__(self, base_url=None):
        self.base_url = base_url if base_url else BASE_URL

    def api_request(self, url, method='GET', headers={}, data=None, isJson=True):
        if isJson:
            headers['Content-Type'] = 'application/json'
        else:
            data = urllib.urlencode(data)
        req = urllib2.Request(self.base_url + url, headers=headers)
        if method in ['PUT', 'DELETE', 'POST', 'GET']:
            req.get_method = lambda: method
        response = urllib2.urlopen(req, json.dumps(data))
        return response


def create():
    app = "/alarm/trigger/create"
    jsondata = {
        'sys_triggers':
            {
                'user_id': 'abcd',
                'trigger_name': 'test',
                'trigger_type': 'instance',
                'expression': 'a=b',
                'mobile': 'True',
                'email': 'False'
            }
    }
    response = RequestClient().api_request(url=app, method='POST', data=jsondata)
    clean_data = json.loads(response.read())
    print clean_data


def update(id):
    app = "/alarm/trigger/update/" + str(id)
    jsondata = {
        'sys_triggers':
            {
                'user_id': 'abcd',
                'trigger_name': 'testupdate',
                'trigger_type': 'instance',
                'expression': 'a!=b',
                'mobile': 'True',
                'email': 'False'
            }
    }
    response = RequestClient().api_request(url=app, method='PUT', data=jsondata)
    clean_data = json.loads(response.read())
    print clean_data


def delete(id):
    app = "/router/delete/" + str(id)
    response = RequestClient().api_request(url=app, method='DELETE')
    clean_data = json.loads(response.read())
    print clean_data


def get_by_user_id(id):
    app = '/alarm/trigger/getTriggerByUserID/' + str(id)
    response = RequestClient().api_request(url=app, method='GET')
    clean_data = json.loads(response.read())
    print clean_data


def agent_detail(id):
    app = '/agent/detail/' + str(id)
    response = RequestClient().api_request(url=app, method='GET')
    clean_data = json.loads(response.read())
    print clean_data


def agent_list():
    app = '/agent/list'
    response = RequestClient().api_request(url=app, method='GET')
    clean_data = json.loads(response.read())
    print clean_data


if __name__ == '__main__':
    # create()
    agent_detail(1)
#    agent_list()
    # delete(3)
    # #     get_by_user_id('abcd')