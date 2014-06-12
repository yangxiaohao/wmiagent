#coding:utf-8
import win32serviceutil
import win32service
import win32event
import win32evtlogutil
import time
import json
import urllib2
import traceback
from WinPollster import WinPollster

def wr_data(url, obj):
    '''Write data/parameter through HttpServer.'''
    data = json.dumps(obj)
    res = None
    try:
        print data
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        print 'xxxx1xxxxx'
        res = urllib2.urlopen(req, timeout=5)
        print 'xxxx2xxxxx'
        return res.read()
    except urllib2.URLError, e:
        print 'xxxxxxxxx' + e.reason
    finally:
        if res:
            res.close()

if __name__=='__main__':
    _wp = WinPollster()
    _wp.update()
    for i in range(1,100):
        time.sleep(1)
        _wp.update()
        wr_obj = _wp.combine()
        print wr_obj['data']['CPUUsagePollster']['data']
    _wr_url = 'http://127.0.0.1:8655/'
    print wr_data('%s%s' %(_wr_url, 'setdata'), wr_obj)
