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
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        res = urllib2.urlopen(req, timeout=5)
        return res.read()
    except Exception, err:
        return False
    finally:
        if res:
            res.close()

class PollManager(win32serviceutil.ServiceFramework):
    _svc_name_ = "agent_poll_manager"
    _svc_display_name_ = "agent_poll_manager"
    _wp = None
    _wr_url = None
    _poll_intvl = None
    stoppending = False
    counter = 0

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self._wr_url = 'http://127.0.0.1:8655/'
        self._wp = WinPollster()
        self._poll_intvl = 20
        print 'Service start.'
        
    def SvcDoRun(self):
        import servicemanager
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
 
        while True:
            time.sleep(1)
            self.counter = self.counter + 1;
            if self.stoppending == True:
                break
            elif self.counter >= self._poll_intvl:
                self.counter = 0
                self._wp.update()
                wr_obj = self._wp.combine()
                if wr_obj:
                    wr_data('%s%s' %(self._wr_url, 'setdata'), wr_obj)
            else:
                pass
                
        return


    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stoppending = True
        print 'Service stop'
        return

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(PollManager)
