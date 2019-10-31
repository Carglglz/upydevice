#!/usr/bin/env python3

from .upydevice import upy_cmd_c_r, upy_cmd_c_raw_r


class LSM9DS1:
    def __init__(self, device, name='imu'):
        """Phantom LSM9DS1 class"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}

    @upy_cmd_c_r()
    def read_gyro(self):
        return self.dev_dict

    @upy_cmd_c_r()
    def read_accel(self):
        return self.dev_dict

    @upy_cmd_c_r()
    def read_magnet(self):
        return self.dev_dict


class MACHINE:
    def __init__(self, device):
        """Phantom MACHINE class"""
        self.d = device
        self.name = 'machine'
        self.dev_dict = {'name': self.name, 'dev': device}

    @upy_cmd_c_r()
    def unique_id(self):
        return self.dev_dict


class I2C:
    def __init__(self, device, name = 'i2c'):
        """Phantom I2C class"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}

    @upy_cmd_c_r()
    def scan(self):
        return self.dev_dict


class UOS:
    def __init__(self, device, name='uos'):
        """Phantom UOS class"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}

    @upy_cmd_c_r()
    def listdir(self, directory):
        return self.dev_dict

    @upy_cmd_c_raw_r()
    def uname(self):
        return self.dev_dict


class pyb_LED:
    def __init__(self, device, number):
        """Phantom pyb.LED class"""
        self.d = device
        self.name = "{}({})".format('LED', number)
        self.dev_dict = {'name': self.name, 'dev': device}
        self.dev_dict['dev'].cmd('from pyb import LED', silent=True)

    @upy_cmd_c_r(rtn=False)
    def toggle(self):
        return self.dev_dict


class pyb_Timer:
    def __init__(self, device, name):
        """Phantom pyb Timer"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}

    @upy_cmd_c_r(rtn=False)
    def init(self, freq, callback):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def deinit(self):
        return self.dev_dict


class machine_Timer:
    def __init__(self, device, name):
        """Phantom machine Timer"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}
        self.PERIODIC = 1
        self.ONE_SHOT = 0

    @upy_cmd_c_r(rtn=False)
    def init(self, mode, period, callback):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def deinit(self):
        return self.dev_dict


class WLAN:
    def __init__(self, device, name='wlan'):
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}
        self.AUTHMODE_DICT = {0: 'NONE', 1: 'WEP',
                              2: 'WPA PSK', 3: 'WPA2 PSK', 4: 'WPA/WAP2 PSK'}
        self.net_ifconfig = None

    @upy_cmd_c_r()
    def scan(self):
        return self.dev_dict

    @upy_cmd_c_r()
    def ifconfig(self):
        return self.dev_dict

    @upy_cmd_c_r()
    def config(self, *args, **kargs):
        return self.dev_dict

    @upy_cmd_c_r()
    def status(self, rssi):
        return self.dev_dict

    def pty_scan(self):
        netscan_list = self.scan()
        print('=' * 110)
        print('{0:^20} | {1:^25} | {2:^10} | {3:^15} | {4:^15} | {5:^10} '.format(
            'ESSID', 'BSSID', 'CHANNEL', 'RSSI (dB)', 'AUTHMODE', 'HIDDEN'))
        print('=' * 110)
        for netscan in netscan_list:
            auth = self.AUTHMODE_DICT[netscan[4]]
            print('{0:^20} | {1:^25} | {2:^10} | {3:^15} | {4:^15} | {5:^10} '.format(
                netscan[0].decode(), str(netscan[1]), netscan[2], netscan[3],
                auth, str(netscan[5])))

    def get_ifconfig(self):

        ifconf = self.ifconfig()
        self.net_ifconfig = {
            'IP': ifconf[0], 'SUBNET': ifconf[1], 'GATEAWAY': ifconf[2],
            'DNS': ifconf[3]}
        return self.net_ifconfig

    def get_rssi(self):
        return self.status('rssi')


class AP:
    def __init__(self, device, name='ap'):
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}
        self.AUTHMODE_DICT = {0: 'NONE', 1: 'WEP',
                              2: 'WPA PSK', 3: 'WPA2 PSK', 4: 'WPA/WAP2 PSK'}
        self.ap_ifconfig = None
        self.essid = None
        self.conn_devs = None

    @upy_cmd_c_r()
    def status(self, stats):
        return self.dev_dict

    @upy_cmd_c_r()
    def ifconfig(self):
        return self.dev_dict

    @upy_cmd_c_r()
    def config(self, *args, **kargs):
        return self.dev_dict

    def get_ifconfig(self):

        ifconf = self.ifconfig()
        self.ap_ifconfig = {
            'IP': ifconf[0], 'SUBNET': ifconf[1], 'GATEAWAY': ifconf[2], 'DNS': ifconf[3]}
        return self.ap_ifconfig

    def get_essid(self):

        self.essid = self.config('essid')
        return self.essid

    def get_scandevs(self, verbose=True):
        self.conn_devs = self.status('stations')
        if verbose:
            print('Found {} devices'.format(len(self.conn_devs)))
        mac_addr = []
        for dev in self.conn_devs:
            bytdev = bytearray(dev[0])
            mac_ad = ':'.join(str(val) for val in bytdev)
            mac_addr.append(mac_ad)
            if verbose:
                print(f'MAC addres: {mac_ad}')

        return mac_addr
