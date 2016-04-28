#!/usr/bin/python
#_*_ coding: gbk -*-
import sys
import datetime;
import logging
import string;
import cdn.api.reportApi as reportApi
import cdn.api.domainApi as domainApi
logging.basicConfig(level = logging.DEBUG)


def  get_onedomain_cdnflows(domainId): 
    api = reportApi.ReportApi("syscloudcdn", "491fbc7ac81e48544660");                                                                                              
    reportForm = reportApi.ReportForm(); 
    reportForm.dateFrom = "%s 00:00:00"%"2015-12-15"
    reportForm.dateTo = "%s 00:00:00"%"2016-01-01"
    reportForm.reportType = reportApi.REPORT_TYPE_DAILY                                                                                                                                               
    result = api.getFlowReport(reportForm, domainId)                                                  
    flows=result.getFlowPoints()                                                                      
    amount=0;
    if flows is None:
        return 0;
    for each in  flows:
        tmp=string.atof(each.flow.encode())
        amount+=tmp
    return amount
                                                                                                      

if __name__=="__main__":
    flow = 0
    domains = ['1231283']
    for i in domains:
        amount=get_onedomain_cdnflows(i)
        print amount
        flow +=amount
    print "%s %f%s"%("flow",flow,'MB');
    import sys;
    sys.exit(0)
     
