# -*-coding:cp936-*-
import urllib2
req = urllib2.urlopen("https://smarthosts.googlecode.com/svn/trunk/hosts") 
print "getting host for smarthost\n"
hosts="/etc/hosts"
hosts=open(hosts,'w')
hosts.writelines(req)
hosts.close()

import time
time.sleep(2) 
print ("hosts changed")
time.sleep(1)
print "5s"
time.sleep(1)
print "4s"
time.sleep(1)
print "3s"
time.sleep(1)
print "2s"
time.sleep(1)
print "1s"
print "=======have a nice day!======="
time.sleep(2)