__author__ = 'gaga'
#!/usr/bin/python
#_*_ coding: gbk -*-
import sys
import logging
import cdn.api.domainApi as domainApi
logging.basicConfig(level = logging.DEBUG)


def  get_domain_list():
    api = domainApi.DomainApi("syscloudcdn", "491fbc7ac81e48544660");
    domain_list = api.listAll()
    return domain_list


if __name__=="__main__":
    domain_list = get_domain_list()
    for i in domain_list.domainSummarys:
        print 'domain: %s  CNAME: %s  ID: %s  status: %s\n' % (i.domainName, i.cname, i.domainId, i.status)
    sys.exit(0)

