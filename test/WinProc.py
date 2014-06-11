import time
from ctypes import *
from ctypes.wintypes import *

SIZE_T = c_ulong
PWCHAR = c_wchar_p
PCHAR = c_char_p
UCHAR = c_byte

class PERFORMANCE_INFORMATION(Structure):
    _fields_ = [
        ('cb', DWORD),
        ('CommitTotal', SIZE_T),
        ('CommitLimit', SIZE_T),
        ('CommitPeak', SIZE_T),
        ('PhysicalTotal', SIZE_T),
        ('PhysicalAvailable', SIZE_T),
        ('SystemCache', SIZE_T),
        ('KernelTotal', SIZE_T),
        ('KernelPaged', SIZE_T),
        ('KernelNonpaged', SIZE_T),
        ('PageSize', SIZE_T),
        ('HandleCount', DWORD),
        ('ProcessCount', DWORD),
        ('ThreadCount', DWORD),
    ]

class SYSTEM_PROCESSOR_PERFORMANCE_INFORMATION(Structure):
    _fields_ = [
        ('IdleTime', LARGE_INTEGER),
        ('KernelTime', LARGE_INTEGER),
        ('UserTime', LARGE_INTEGER),
        ('Reserved1', LARGE_INTEGER * 2),
        ('Reserved2', ULONG),
    ]

class IP_ADAPTER_ADDRESSES(Structure):
    _fields_ = [
        ('Length', ULONG),
        ('IfIndex', DWORD),
        ('Next', LPVOID),
        ('AdapterName', PCHAR),
        ('FirstUnicastAddress', LPVOID),
        ('FirstAnycastAddress', LPVOID),
        ('FirstMulticastAddress', LPVOID),
        ('FirstDnsServerAddress', LPVOID),
        ('DnsSuffix', PWCHAR),
        ('Description', PWCHAR),
        ('FriendlyName', PWCHAR),
        ('PhysicalAddress', BYTE * 8),
        ('PhysicalAddressLength',  DWORD),
        ('Flags', DWORD),
        ('Mtu', DWORD),
        ('IfType', DWORD),
        ('OperStatus', DWORD),
    ]

class MIB_IFROW(Structure):
    _fields_ = [
        ('wszName', WCHAR * 256),
        ('dwIndex', ULONG),
        ('dwType', ULONG),
        ('dwMtu', DWORD),
        ('dwSpeed', DWORD),
        ('dwPhysAddrLen', DWORD),
        ('bPhysAddr', UCHAR * 8),
        ('dwAdminStatus', DWORD),
        ('dwAdminStatus', WORD),
        ('dwLastChange', DWORD),
        ('dwInOctets', DWORD),
        ('dwInUcastPkts', DWORD),
        ('dwInNUcastPkts', DWORD),
        ('dwInDiscards', DWORD),
        ('dwInErrors', DWORD),
        ('dwInUnknownProtos', DWORD),
        ('dwOutOctets', DWORD),
        ('dwOutUcastPkts', DWORD),
        ('dwOutNUcastPkts', DWORD),
        ('dwOutDiscards', DWORD),
        ('dwOutErrors', DWORD),
        ('dwOutQLen', DWORD),
        ('dwDescrLen', DWORD),
        ('bDescr', UCHAR * 256),
    ]

class DISK_PERFORMANCE(Structure):
    _fields_ = [
        ('BytesRead', LARGE_INTEGER),
        ('BytesWritten', LARGE_INTEGER),
        ('ReadTime', LARGE_INTEGER),
        ('WriteTime', LARGE_INTEGER),
        ('IdleTime', LARGE_INTEGER),
        ('ReadCount', DWORD),
        ('WriteCount', DWORD),
        ('QueueDepth', DWORD),
        ('SplitCount', DWORD),
        ('QueryTime', LARGE_INTEGER),
        ('StorageDeviceNumber', DWORD),
        ('StorageManagerName', WCHAR * 8),
    ]

windows_psapi = WinDLL('psapi.dll')
windows_ntdll = WinDLL('ntdll.dll')
windows_iphlpapi = WinDLL('iphlpapi.dll')


class WinProc(object):
    data = {}
    cache = {}
    def __init__(self):
        self.data['timestamp'] = 0
        self.data['mem'] = {}
        self.data['mem']['load'] = 0
        self.data['mem']['physical_total'] = 0
        self.data['mem']['physical_free'] = 0
        self.data['mem']['cached'] = 0
        self.data['mem']['buffers'] = 0
        self.data['mem']['swap_total'] = 0
        self.data['mem']['swap_free'] = 0
        self.data['cpu'] = {}
        self.data['cpu']['count'] = 0
        self.data['cpu']['load'] = 0
        self.data['cpu']['cpus'] = []
        self.data['net'] = {}
        self.data['net']['count'] = 0
        self.data['net']['rate_out'] = 0
        self.data['net']['rate_in'] = 0
        self.data['net']['bytes_out'] = 0
        self.data['net']['bytes_in'] = 0
        self.data['net']['packets_out'] = 0
        self.data['net']['packets_in'] = 0
        self.data['net']['rate_packets_out'] = 0
        self.data['net']['rate_packets_in'] = 0
        self.data['disk'] = {}
        self.data['disk']['count'] = 0
        self.data['disk']['total_space_free'] = 0
        self.data['disk']['total_space_total'] = 0
        self.data['disk']['total_rate_read'] = 0
        self.data['disk']['total_rate_writen'] = 0
        
        self.cache['proc_current'] = {}
        self.cache['proc_last'] = {}
        return

    def fetch_cpu(self):
        dict = {}
        dict['timestamp'] = time.time()

        size = ULONG(1)
        sppis = (SYSTEM_PROCESSOR_PERFORMANCE_INFORMATION * 16)()
        windows_ntdll.NtQuerySystemInformation(8, byref(sppis), sizeof(sppis), byref(size))
        count = size.value/sizeof(SYSTEM_PROCESSOR_PERFORMANCE_INFORMATION)
        dict['count'] = int(count)

        dict['cpus'] = []
        for i in range(0, count):
            cpuinfo = {'UserTime': sppis[i].UserTime, 'KernelTime': sppis[i].KernelTime, 'IdleTime': sppis[i].IdleTime}
            dict['cpus'].append(cpuinfo)
        dict['count'] = count
        self.cache['proc_current']['cpu'] = dict
        return dict

    def fetch_mem(self):
        dict = {}
        dict['timestamp'] = time.time()
        
        data_dict = {}
        pi = PERFORMANCE_INFORMATION();
        pi.cb = sizeof(pi);
        windows_psapi.GetPerformanceInfo(byref(pi), sizeof(pi));
        
        dict['PhysicalTotal'] = pi.PhysicalTotal * pi.PageSize
        dict['PhysicalAvailable'] = pi.PhysicalAvailable * pi.PageSize
        dict['SystemCache'] = pi.SystemCache * pi.PageSize
        dict['KernelPaged'] = pi.KernelPaged * pi.PageSize
        dict['CommitLimit'] = pi.CommitLimit * pi.PageSize
        dict['CommitTotal'] = pi.CommitTotal * pi.PageSize

        self.cache['proc_current']['mem'] = dict
        return dict
    
    def fetch_net(self):
        dict = {}
        dict['timestamp'] = time.time()
        
        size = ULONG(1)
        windows_iphlpapi.GetAdaptersAddresses(0, 0, 0, 0, byref(size));
        lpvoid = windll.kernel32.HeapAlloc(windll.kernel32.GetProcessHeap(), 0, size.value)
        windows_iphlpapi.GetAdaptersAddresses(0, 0, 0, lpvoid, byref(size));
        
        dict['nets'] = []
        iaa = cast(lpvoid, POINTER(IP_ADAPTER_ADDRESSES))[0]
        count = 0
        while(True):
            # UP and ETHERNET
            # Enable iaa.IfType == 71 for IEEE80211
            if iaa.OperStatus == 1 and iaa.IfType == 6:
                mi = MIB_IFROW()
                mi.dwIndex = iaa.IfIndex;
                windows_iphlpapi.GetIfEntry(byref(mi));
                netinfo = {'AdapterName': iaa.AdapterName, 'FriendlyName': str(iaa.FriendlyName), 'dwInOctets': mi.dwInOctets, 'dwOutOctets': mi.dwOutOctets, 'dwInUcastPkts': mi.dwInUcastPkts, 'dwOutUcastPkts': mi.dwOutUcastPkts, 'dwInNUcastPkts': mi.dwInNUcastPkts, 'dwOutNUcastPkts': mi.dwOutNUcastPkts}
                dict['nets'].append(netinfo)
                count = count + 1
            
            if iaa.Next == None:
                break
            iaa = cast(iaa.Next, POINTER(IP_ADAPTER_ADDRESSES))[0]
        dict['count'] = count
        self.cache['proc_current']['net'] = dict
        return dict

    def fetch_disk(self):
        dict = {}
        dict['timestamp'] = time.time()
        
        drives = windll.kernel32.GetLogicalDrives();
        driveid = ord('A')
        dict['disks'] = []
        count = 0
        while drives != 0:
            if (drives & 1):
                drive = chr(driveid);
                drive_path = '\\\\.\\' + drive +':'
                
                device_handle = windll.kernel32.CreateFileA(drive_path, 0, 0x01 | 0x02, 0, 0x03, 0, 0);
                device_type = windll.kernel32.GetDriveTypeA(drive_path + '\\');
                if (device_type == 3 and device_handle != -1):
                    FreeBytesAvailable = ULARGE_INTEGER()
                    TotalNumberOfBytes = ULARGE_INTEGER()
                    TotalNumberOfFreeBytes = ULARGE_INTEGER()
                    
                    dp = DISK_PERFORMANCE()
                    size =  DWORD();
                    # IOCTL_DISK_PERFORMANCE
                    windll.kernel32.DeviceIoControl(device_handle, 458784, 0, 0, byref(dp), sizeof(dp), byref(size), 0);
                    windll.kernel32.GetDiskFreeSpaceExA(drive_path + '\\', byref(FreeBytesAvailable), byref(TotalNumberOfBytes), byref(TotalNumberOfFreeBytes));
                    diskinfo = {'DriveName': drive +':','TotalNumberOfBytes': TotalNumberOfBytes.value, 'TotalNumberOfFreeBytes': TotalNumberOfFreeBytes.value, 'BytesRead':dp.BytesRead, 'BytesWritten':dp.BytesWritten}
                    dict['disks'].append(diskinfo)
                    count = count + 1
            drives = drives >> 1
            driveid = driveid + 1
        dict['count'] = count
        self.cache['proc_current']['disk'] = dict
        return dict

    def update(self):
      
        self.fetch_net()
        self.fetch_mem()
        self.fetch_cpu()
        self.fetch_disk()
        
        self.cache['proc_current']
        
        dict = self.cache['proc_current']['mem'];
        
        self.cache['proc_last']['mem'] = dict
        self.data['mem']['physical_total'] = dict['PhysicalTotal']
        self.data['mem']['physical_free'] = dict['PhysicalAvailable']
        self.data['mem']['cached'] = dict['SystemCache']
        self.data['mem']['buffers'] = dict['KernelPaged'] 
        self.data['mem']['swap_total'] = dict['CommitLimit'] 
        self.data['mem']['swap_free'] = dict['CommitLimit'] - dict['CommitTotal']
        self.data['mem']['load'] = 1 - float (dict['PhysicalAvailable']) / float (dict['PhysicalTotal'])
        
        
        dict = self.cache['proc_current']['cpu'];
        timespan = dict['timestamp'] - self.data['timestamp']
        if (timespan > 1):
            
            # init
            if self.data['cpu']['count'] != dict['count']:
                self.data['cpu']['cpus'] = []
                self.data['cpu']['count'] = dict['count']
                total_load = 0
                for cpu in dict['cpus']:
                    load = float(cpu['IdleTime']) / float(cpu['KernelTime'] + cpu['UserTime'])
                    load = 1 / ( 1 + load )
                    self.data['cpu']['cpus'].append( {'load': load} )
                    total_load = total_load + load
                self.data['cpu']['load'] = total_load / dict['count']
            # upate
            else:
                total_load = 0
                for i in range(0, dict['count']):
                    cpu_current = self.cache['proc_current']['cpu']['cpus'][i]
                    cpu_last = self.cache['proc_last']['cpu']['cpus'][i]
                    load = float(cpu_current['IdleTime'] - cpu_last['IdleTime']) / float(cpu_current['KernelTime'] + cpu_current['UserTime'] - cpu_last['KernelTime'] - cpu_last['UserTime'] )
                    load = 1 / ( 1 + load )
                    self.data['cpu']['cpus'].append( {'load': load} )
                    total_load = total_load + load
                self.data['cpu']['load'] = total_load / dict['count'] 
            self.cache['proc_last']['cpu'] = dict
            
            
        dict = self.cache['proc_current']['net'];
        timespan = dict['timestamp'] - self.data['timestamp']
        if (timespan > 1):
        
            rate_out = 0
            rate_in = 0;
            rate_packets_out = 0
            rate_packets_in = 0;
            bytes_out = 0
            bytes_in = 0
            packets_out = 0
            packets_in = 0
            
            for i in range(0, dict['count']):
                net_current = self.cache['proc_current']['net']['nets'][i]
                #net_last = self.cache['proc_last']['net']['nets'][i]
                bytes_in += net_current['dwInOctets']
                bytes_out += net_current['dwOutOctets']
                packets_in += net_current['dwInUcastPkts'] + net_current['dwInNUcastPkts']
                packets_out += net_current['dwOutUcastPkts'] + net_current['dwOutNUcastPkts']
                
            # init
            if not self.cache['proc_last'].has_key('net'):
                rate_in = float(bytes_in)/timespan
                rate_out = float(bytes_out)/timespan
                rate_packets_in = float(packets_in)/timespan
                rate_packets_out = float(packets_out)/timespan
            else:
                rate_in = float(bytes_in - self.data['net']['bytes_in'])/timespan
                rate_out = float(bytes_out - self.data['net']['bytes_out'])/timespan
                rate_packets_in = float(packets_in - self.data['net']['packets_in'])/timespan
                rate_packets_out = float(packets_out - self.data['net']['packets_out'])/timespan

            self.cache['proc_last']['net'] = dict
                
            self.data['net']['rate_out'] = rate_out
            self.data['net']['rate_in'] = rate_in
            self.data['net']['bytes_out'] = bytes_out
            self.data['net']['bytes_in'] = bytes_in
            self.data['net']['packets_out'] = packets_out
            self.data['net']['packets_in'] = packets_in
            self.data['net']['rate_packets_out'] = rate_packets_out
            self.data['net']['rate_packets_in'] = rate_packets_in
            
        dict = self.cache['proc_current']['disk'];
        timespan = dict['timestamp'] - self.data['timestamp']
        if (timespan > 1):
            
            # init
            if self.data['disk']['count'] != dict['count']:
                self.data['disk']['disks'] = []
                self.data['disk']['count'] = dict['count']

                total_space_free = 0
                total_space_total = 0
                total_rate_read = 0
                total_rate_writen = 0
                
                for disk in dict['disks']:
                    space_free = disk['TotalNumberOfFreeBytes']
                    space_total = disk['TotalNumberOfBytes']
                    rate_read = float(disk['BytesRead'])/timespan 
                    rate_writen = float(disk['BytesWritten'])/timespan 
                    self.data['disk']['disks'].append( {'drive':disk['DriveName'], 'space_free':space_free, 'space_total':space_total, 'rate_read':rate_read, 'rate_writen':rate_writen} )
                    total_space_free += space_free
                    total_space_total += space_total
                    total_rate_read += rate_read
                    total_rate_writen += rate_writen
                self.data['disk']['total_space_free'] = total_space_free
                self.data['disk']['total_space_total'] = total_space_total
                self.data['disk']['total_rate_read'] = total_rate_read
                self.data['disk']['total_rate_writen'] = total_rate_writen
            # upate
            else:
                total_space_free = 0
                total_space_total = 0
                total_rate_read = 0
                total_rate_writen = 0
                
                total_load = 0
                for i in range(0, dict['count']):
                    disk_current = self.cache['proc_current']['disk']['disks'][i]
                    disk_last = self.cache['proc_last']['disk']['disks'][i]
                    
                    space_free = disk_current['TotalNumberOfFreeBytes']
                    space_total = disk_current['TotalNumberOfBytes']
                    rate_read = float(disk_current['BytesRead'] - disk_last['BytesRead'])/timespan 
                    rate_writen = float(disk_current['BytesWritten'] - disk_last['BytesWritten'])/timespan 
                    self.data['disk']['disks'].append( {'space_free':space_free, 'space_total':space_total, 'rate_read':rate_read, 'rate_writen':rate_writen} )
                    total_space_free += space_free
                    total_space_total += space_total
                    total_rate_read += rate_read
                    total_rate_writen += rate_writen
                self.data['disk']['total_space_free'] = total_space_free
                self.data['disk']['total_space_total'] = total_space_total
                self.data['disk']['total_rate_read'] = total_rate_read
                self.data['disk']['total_rate_writen'] = total_rate_writen
                
            self.cache['proc_last']['disk'] = dict 
            
        self.data['timestamp'] = time.time()

    def debug(self):
        self.update()
        ## print self.data
        print 'MEM:'
        print self.data['mem']['load']
        print 'CPU:'
        print self.data['cpu']['load']
        print 'NET:'
        print self.data['net']['rate_in']
        print self.data['net']['rate_out']
        print 'DISK:'
        print self.data['disk']['total_rate_read']
        print self.data['disk']['total_rate_writen']
        print ''

if __name__=='__main__':
    wp = WinProc()
    wp.debug()
    time.sleep(0.4)
    wp.debug()
    time.sleep(0.8)
    wp.debug()
    time.sleep(1.6)
    wp.debug()
    time.sleep(3.2)
    wp.debug()
    time.sleep(3.2)
    wp.debug()
    for i in range(0, 15):
        time.sleep(3.2)
        wp.debug()