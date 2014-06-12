import os
import sys
import platform
import time
import traceback
from WinProc import *


class WinPollster(object):
    hostname = ''
    ipaddress = None
    winproc = WinProc()
    def __init__(self):
        self.winproc.update()
        return

    def update(self):
        self.winproc.update()
        return

    def get_cpu(self):
        data_dict = {}
        winproc_cpu = self.winproc.data['cpu']
        for i in range(0, winproc_cpu['count']):
            data_dict['cpu' + str(i)] = {'volume': round(winproc_cpu['cpus'][i]['load'] * 100, 2), 'unit':'%'}
        data_dict['cpu'] = {'volume':round(winproc_cpu['load'] * 100, 2), 'unit':'%'}
        return {'data':data_dict, 'timestamp':time.asctime(time.localtime())}
 
    def get_mem(self):
        data_dict = {}
        winproc_mem = self.winproc.data['mem']
        data_dict["MemTotal"] = {'volume': round(float(winproc_mem['physical_total']) / (1024*1024), 2), 'unit':'MB'}
        data_dict["MemFree"] = {'volume': round(float(winproc_mem['physical_free']) / (1024*1024), 2), 'unit':'MB'}
        data_dict["Cached"] = {'volume':  0, 'unit':'MB'} # round(float(winproc_mem['cached'])  / (1024*1024), 2)
        data_dict["Buffers"] = {'volume': 0, 'unit':'MB'} #round(float(winproc_mem['buffers'])  / (1024*1024), 2)
        data_dict["SwapTotal"] = {'volume': round(float(winproc_mem['swap_total']) / (1024*1024), 2), 'unit':'MB'}
        data_dict["SwapFree"] = {'volume': round(float(winproc_mem['swap_free']) / (1024*1024), 2), 'unit':'MB'}
        return {'data':data_dict, 'timestamp':time.asctime(time.localtime())}

    def get_disk(self):
        data_dict = {}
        winproc_disk = self.winproc.data['disk']
        
        data_dict['total_available'] = round(float(winproc_disk['total_space_free']) / (1024*1024*1024), 2)
        data_dict['total_capacity'] = round(float(winproc_disk['total_space_total']) / (1024*1024*1024), 2)
        data_dict['total_free'] = round(float(winproc_disk['total_space_free']) / (1024*1024*1024), 2)

        for i in range(0, winproc_disk['count']):
            disk = winproc_disk['disks'][i];
            dev_tmp = {}
            dev_tmp['dev'] = disk['drive']
            dev_tmp['available'] = {'volume':round(float(disk['space_free']) / (1024*1024*1024), 2), 'unit':'GB'}
            dev_tmp['capacity'] = {'volume':round(float(disk['space_total']) / (1024*1024*1024), 2), 'unit':'GB'}
            dev_tmp['free'] = {'volume':round(float(disk['space_free']) / (1024*1024*1024), 2), 'unit':'GB'}
            dev_tmp['fstype'] = ''
            dev_tmp['mnt'] = ''
            dev_tmp['used'] = round(disk['space_free'] / disk['space_total'], 2)
            dev_tmp['io_stat'] = {}
            dev_tmp['io_stat']['r/s'] = {'volume':round(float(disk['rate_read']), 2), 'unit':''}
            dev_tmp['io_stat']['w/s'] = {'volume':round(float(disk['rate_writen']), 2), 'unit':''}
            dev_tmp['io_stat']['rkB/s'] = {'volume':round(float(disk['rate_read']) / 1024, 2), 'unit':'KB/s'}
            dev_tmp['io_stat']['wkB/s'] = {'volume':round(float(disk['rate_writen']) / 1024, 2), 'unit':'KB/s'}
                
            data_dict[disk['drive']] = dev_tmp
        return {'data':data_dict, 'timestamp':time.asctime(time.localtime())}

    def get_net(self):
        data_dict = {}
        winproc_net = self.winproc.data['net']
        data_dict['net_bytes_in'] = {'volume':round(winproc_net['rate_in'], 2), 'unit':'B/s'}
        data_dict['net_bytes_in_sum'] = {'volume':winproc_net['bytes_in'], 'unit':'B'}
        data_dict['net_bytes_out'] = {'volume':round(winproc_net['rate_out'], 2), 'unit':'B/s'}
        data_dict['net_bytes_out_sum'] = {'volume':winproc_net['bytes_out'], 'unit':'B'}
        data_dict['net_pkts_in'] = {'volume':round(winproc_net['rate_packets_in'], 2), 'unit':'p/s'}
        data_dict['net_pkts_out'] = {'volume':round(winproc_net['rate_packets_out'], 2), 'unit':'p/s'}

        return {'data':data_dict, 'timestamp':time.asctime(time.localtime())}

    def combine(self):
        combine_data = {}
        combine_data['data'] = {}
        combine_data['hostname'] = self.hostname
        try:
            combine_data['data']['CPUUsagePollster'] = self.get_cpu()
            combine_data['data']['DiskUsagePollster'] = self.get_disk()
            combine_data['data']['MemInfoPollster'] = self.get_mem()
            combine_data['data']['NetStatPollster'] = self.get_net()

            if self.ipaddress:
                combine_data['ip_address'] = self.ipaddress
            else:
                combine_data['ip_address'] = '127.0.0.1'
            combine_data['status'] = 'NORMAL'
        except Exception,err:
            print err
            print traceback.format_exc()
            combine_data['status'] = 'ERROR'
        finally:
            combine_data['timestamp'] = time.asctime(time.localtime()) 
            return combine_data

if __name__=='__main__':
    wp = WinPollster()
    print wp.combine()
    
    '''
    for i in range(0, 32):
        time.sleep(1)
        wp.update()
        print wp.combine()
    '''
    
