__author__ = 'gaga'
#!/usr/bin/python
#_*_ coding: gbk -*-
import sys
import logging
import cdn.api.domainApi as domainApi
logging.basicConfig(level = logging.DEBUG)


def  get_domain_info(domainId):
    api = domainApi.DomainApi("syscloudcdn", "491fbc7ac81e48544660");
    domain = api.find(domainId)
    return domain


if __name__=="__main__":
    for i in ['219151','1222505']:
        domain = get_domain_info('1222505')

    sys.exit(0)
