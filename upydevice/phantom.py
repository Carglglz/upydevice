#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2019-10-30T23:49:59+00:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-11-16T22:41:08+00:00


"""Phantom classes collection"""

from .upydevice import (upy_cmd_c_r, upy_cmd_c_raw_r, upy_cmd_c_r_in_callback,
                        upy_cmd_c_r_nb, upy_cmd_c_r_nb_in_callback)
import time
import socket
import struct
import sys
from datetime import datetime
from binascii import hexlify
import json
import os


# MICROPYTHON DEFAULT CLASSES

class MACHINE:
    def __init__(self, device):
        """Phantom MACHINE class"""
        self.d = device
        self.name = 'machine'
        self.dev_dict = {'name': self.name, 'dev': device}

    @upy_cmd_c_r()
    def unique_id(self):
        return self.dev_dict


# PIN

class Pin:
    def __init__(self, device, name, mode='OUT', number=0, init=False):
        """Phantom machine.Pin class"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}
        # CONST
        self.IRQ_FALLING = 2
        self.IRQ_RISING = 1
        self.IRQ_BOTH = 3
        self.OUT = 3
        self.IN = 1
        self.OPEN_DRAIN = 7
        self.PULL_HOLD = 4
        self.PULL_DOWN = 1
        self.WAKE_LOW = 4
        self.WAKE_HIGH = 5
        if init:
            if mode == 'IN':
                self.d.cmd("{}=Pin({}, {})".format(
                    name, number, self.IN), silent=True)
            if mode == 'OUT':
                self.d.cmd("{}=Pin({}, {})".format(
                    name, number, self.OUT), silent=True)

    @upy_cmd_c_r()
    def value(self, *args):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def on(self):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def off(self):
        return self.dev_dict

    def toggle(self):
        self.value(not self.value())

    @upy_cmd_c_r(rtn=False)
    def irq(self, trigger, handler, priority=1, wake=None, hard=False):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def mode(self, mode):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def pull(self, pull):
        return self.dev_dict


# I2C

class I2C:
    def __init__(self, device, name='i2c', init=False, scl=None, sda=None, freq=400000):
        """Phantom I2C class"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}
        if init:
            self.d.cmd('from machine import I2C,Pin; {} = I2C(scl=Pin({}), sda=Pin({}), freq={})'.format(
                name, scl, sda, freq), silent=True)

    @upy_cmd_c_r()
    def scan(self):
        return self.dev_dict

    # Primitive I2C operations (on I2C software only)

    @upy_cmd_c_r(rtn=False)
    def start(self):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def stop(self):
        return self.dev_dict

    @upy_cmd_c_r()
    def readinto(self, buf, nack=True):
        return self.dev_dict

    @upy_cmd_c_r()
    def write(self, buf):
        return self.dev_dict

    # Standard bus operations

    @upy_cmd_c_r()
    def readfrom(self, addr, nbytes, stop=True):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def readfrom_into(self, addr, buf, stop=True):
        return self.dev_dict

    @upy_cmd_c_r()
    def writeto(self, addr, buf, stop=True):
        return self.dev_dict

    @upy_cmd_c_r()
    def writevto(self, addr, vector, stop=True):
        return self.dev_dict

    # Memory operations
    @upy_cmd_c_r()
    def readfrom_mem(self, addr, memaddr, nbytes, addrsize=8):
        return self.dev_dict

    @upy_cmd_c_r()
    def readfrom_mem_into(self, addr, memaddr, buf, addrsize=8):
        return self.dev_dict

    @upy_cmd_c_r()
    def writeto_mem(self, addr, memaddr, buf, addrsize=8):
        return self.dev_dict


# UOS

class UOS:
    def __init__(self, device, name='uos'):
        """Phantom UOS class"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}

    @upy_cmd_c_r()
    def listdir(self, directory):
        return self.dev_dict

    @upy_cmd_c_r()
    def getcwd(self):
        return self.dev_dict

    @upy_cmd_c_r()
    def mkdir(self, directory):
        return self.dev_dict

    @upy_cmd_c_r()
    def rmdir(self, directory):
        return self.dev_dict

    @upy_cmd_c_r()
    def chdir(self, directory):
        return self.dev_dict

    @upy_cmd_c_r()
    def remove(self, file):
        return self.dev_dict

    @upy_cmd_c_raw_r()
    def uname(self):
        return self.dev_dict

#############################################


# PYBOARD CLASSES

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


class pyb_Servo:
    def __init__(self, device, name, number=None, init=False):
        """Phantom pyb Servo"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}
        if init:
            self.d.cmd('import pyb; {} = pyb.Servo({})'.format(name, number))

    @upy_cmd_c_r()
    def angle(self, *args, **kargs):  # to allow no args
        """args: angle, time"""
        return self.dev_dict

    @upy_cmd_c_r()
    def speed(self, *args, **kargs):  # to allow no args
        """args: speed, time"""
        return self.dev_dict

    @upy_cmd_c_r()
    def pulse_width(self, *args, **kargs):  # to allow no args
        """args: value"""
        return self.dev_dict

    @upy_cmd_c_r()
    def calibration(self, *args, **kargs):  # to allow no args
        """args: pulse_min, pulse_max, pulse_centre,[pulse_angle_90, pulse_speed_100]"""
        return self.dev_dict


#############################################


# TIMER

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


# NETWORK WLAN

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
            vals = hexlify(netscan[1]).decode()
            bssid = ':'.join([vals[i:i+2] for i in range(0, len(vals), 2)])
            print('{0:^20} | {1:^25} | {2:^10} | {3:^15} | {4:^15} | {5:^10} '.format(
                netscan[0].decode(), bssid, netscan[2], netscan[3],
                auth, str(netscan[5])))

    def get_ifconfig(self):

        ifconf = self.ifconfig()
        self.net_ifconfig = {
            'IP': ifconf[0], 'SUBNET': ifconf[1], 'GATEAWAY': ifconf[2],
            'DNS': ifconf[3]}
        return self.net_ifconfig

    def get_rssi(self):
        return self.status('rssi')


# NETWORK AP

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
            'IP': ifconf[0], 'SUBNET': ifconf[1], 'GATEAWAY': ifconf[2],
            'DNS': ifconf[3]}
        return self.ap_ifconfig

    def get_essid(self):

        self.essid = self.config('essid')
        return self.essid

    def get_scandevs(self, verbose=True):  # NOT COMPATIBLE WITH ESP8266
        self.conn_devs = self.status('stations')
        if verbose:
            print('Found {} devices'.format(len(self.conn_devs)))
        mac_addr = []
        for dev in self.conn_devs:
            bytdev = bytearray(dev[0])
            mac_ad = ':'.join(str(val) for val in bytdev)
            mac_addr.append(mac_ad)
            if verbose:
                try:
                    print(f'MAC address: {mac_ad}')
                except Exception as e:
                    print("MAC address: {}".format(mac_ad))
                    pass

        return mac_addr

# NETWORK SOCKETS
# U_SOCKET

#############################################
# CUSTOM CLASSES (UPYDEVICE UTILS)


# IRQ UTILS

class IRQ_MG:
    def __init__(self, device, name, init_soc=False, port=8005, p_format='f',
                 n_vars=3, sensor=None, log_dir=None, logg=None):
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}
        self.soc = None
        self.port = port
        if init_soc:
            self.soc = socket_server(port=self.port)
        self.p_format = p_format
        self.n_vars = n_vars
        self.data_length = struct.calcsize(self.p_format*self.n_vars)
        self.buffer = []
        self.log_dir = log_dir
        # self.sensor, class U_IMU_IRQ (read_data, set_mode)

    @upy_cmd_c_r(rtn=False)
    def reset_flag(self):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def reset_flag_counter(self):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def set_irq_msg(self, msg):
        return self.dev_dict

    @upy_cmd_c_r()
    def irq_state(self):
        return self.dev_dict

    @upy_cmd_c_r(debug=True)  # to check prints
    def wait_irq(self, reset=True):
        return self.dev_dict

    @upy_cmd_c_r_nb(debug=True)  # to check prints
    def wait_async_irq(self, reset=True):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def buzz_beep(self, sleeptime, ntimes, ntimespaced, fq):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def led_blink(self, sleeptime, ntimes, ntimespaced):
        return self.dev_dict

    @upy_cmd_c_r_in_callback(rtn=False)
    def active_button(self, callback, **kargs):
        return self.dev_dict

    @upy_cmd_c_r_in_callback(rtn=False)
    def active_button_rev(self, callback, **kargs):
        return self.dev_dict

    def async_irq_listener_loop(self, on_irq, func_loop=None, wait_time=0.05):
        self.wait_async_irq()
        self.d.output = None
        while self.d.output is None:
            if func_loop is not None:
                func_loop()
            self.d.get_opt()
            time.sleep(wait_time)

        # check condition in self.d.output
        on_irq(self.d.output)

    # THIS CAN HANG WEBREPL (BETTER USE SOCKETS) --> continuos_async_soc...
    def continuos_async_irq_loop(self, on_irq, func_loop=None, wait_time=0.05):
        while True:
            try:
                self.async_irq_listener_loop(on_irq, func_loop,
                                             wait_time=wait_time)
                time.sleep(1)
            except KeyboardInterrupt:
                break

    def async_irq_listener_check(self, on_irq, waiting=True):
        if not waiting:
            self.wait_async_irq()
            self.d.output = None
        if self.d.output is None:
            self.d.get_opt()
            if self.d.output is None:
                return False
            else:
                # check condition in self.d.output
                on_irq(self.d.output)
                return self.d.output
        else:
            # check condition in self.d.output
            on_irq(self.d.output)
            return self.d.output

    # SOCKETS MESSAGING

    @upy_cmd_c_r_nb(debug=True)
    def connect_SOC(self, host, port):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def disconnect_SOC(self):
        return self.dev_dict

    def start_server(self):
        self.connect_SOC(self.soc.host, self.port)
        self.soc.start_SOC()

    def stop_server(self):
        self.disconnect_SOC()
        self.soc.conn.close()
        self.soc.serv_soc.close()

    def soc_recv_message(self):
        try:
            data = self.soc.conn.recv(self.data_length)
            data_unpack = struct.unpack(self.p_format*self.n_vars, data)
            self.d.output = data_unpack
            return data_unpack
        except Exception as e:
            return None

    # + LOG_OPTION
    def async_soc_irq_listener_loop(self, on_irq, func_loop=None,
                                    wait_time=0.05, log_nf=False,
                                    buffer=False, log=False,
                                    filename=None, tag=None):
        if log_nf:
            log = True
            if filename is None:
                filename = 'irq_{}_log.txt'.format(self.name)
            self.lognow_shot('irq', filename=filename, rtn=False)
        self.d.output = None
        while self.d.output is None:
            if func_loop is not None:
                func_loop()
            self.d.output = self.soc_recv_message()
            time.sleep(wait_time)

        # check condition in self.d.output
        on_irq(self.d.output)   # PRINT + LOG_OPTION + BUFFER
        if log:
            self.log_data_shot(filename, self.d.output, n_tag=tag)
        if buffer:
            self.log_data_shot_buff(self.d.output, n_tag=tag)

    # + LOG_OPTION
    def continuos_async_soc_irq_loop(self, on_irq, func_loop=None,
                                     wait_time=0.05, filename=None,
                                     log=False, tag=None, buffer=False):
        if log:
            if filename is None:
                filename = 'irq_{}_log.txt'.format(self.name)
            self.lognow_shot('irq', filename=filename, rtn=False)
        while True:
            try:
                self.async_soc_irq_listener_loop(
                    on_irq, func_loop, wait_time=wait_time, log=log,
                    filename=filename, tag=tag, buffer=buffer)
                time.sleep(wait_time)
            except KeyboardInterrupt:
                break

    # CALLBACKS

    def buzzer_callback(self, x):
        pass

    def buzzer_callback_rev(self, x):
        pass

    def led_callback(self, x):
        pass

    def led_callback_rev(self, x):
        pass

    def msg_callback(self, x):
        pass

    def msg_callback_rev(self, x):
        pass

    def sensor_callback(self, x):
        pass

    def sensor_soc_callback(self, x):
        pass

    def data_print(self, x):
        try:
            print(self.data_print_msg.format(*x, self.header['UNIT']))
        except Exception as e:
            pass

    # LOG methods

    # FILE LOG

    def lognow_shot(self, sensor_mode, filename=None, debug=True, rtn=True):
        file_name = filename
        if debug:
            print('Saving file {} ...'.format(file_name))
        with open(file_name, 'w') as file_log:
            header_vars = self.header['VAR'].copy()
            header_vars.append('TS')
            header_unit = self.header['UNIT']
            SHOT_HEADER = {'VAR': header_vars, 'UNIT': header_unit}
            file_log.write(json.dumps(SHOT_HEADER))
            file_log.write('\n')
        if rtn:
            return file_name

    def log_data_shot(self, filename, data, n_tag=None):
        try:
            data_pack = dict(zip(self.header['VAR']+['TS'],
                                 [val for val in data]+[datetime.now().strftime("%m_%d_%Y_%H_%M_%S")]))
            if n_tag is not None:
                data_pack = dict(zip(self.header['VAR']+['TS'],
                                     [val for val in data]+[n_tag]))
            with open(filename, 'a') as file_log:
                file_log.write(json.dumps(data_pack))
                file_log.write('\n')
        except Exception as e:
            pass

    # BUFFER LOG

    def log_data_shot_buff(self, data, n_tag=None):
        try:
            data_pack = dict(zip(self.header['VAR']+['TS'],
                                 [val for val in data]+[datetime.now().strftime("%m_%d_%Y_%H_%M_%S")]))
            if n_tag is not None:
                data_pack = dict(zip(self.header['VAR']+['TS'],
                                     [val for val in data]+[n_tag]))
            self.buffer.append(json.dumps(data_pack))
        except Exception as e:
            pass

    def read_buffer_shot(self):
        list_of_vars = {var: [] for var in self.header['VAR']+['TS']}
        for message in self.buffer:
            try:
                vals = json.loads(message)
                for key in vals.keys():
                    list_of_vars[key].append(vals[key])
            except Exception as e:
                pass
        return (list_of_vars)

    def flush_buffer(self):
        self.buffer = []


# TCP STREAMER
class STREAMER:
    def __init__(self, device, name, init_soc=False, port=8005, p_format='f',
                 n_vars=3, log_dir=None, chunk_buffer_size=20, soc_timeout=1,
                 logg=None):
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}
        self.soc = None
        self.port = port
        if init_soc:
            self.soc = socket_server(port=self.port, soc_timeout=soc_timeout,
                                     logg=logg)
        self.p_format = p_format
        self.n_vars = n_vars
        self.data_length = struct.calcsize(self.p_format*self.n_vars)
        self.chunk_buffer_size = chunk_buffer_size
        self.chunk_buffer_data_length = struct.calcsize(
            self.p_format*self.chunk_buffer_size)
        self.fq = None
        self.log_dir = log_dir
        self.buffer = []
        self.time_test = 0
        self._json_errors = 0
        self._json_buffer = ' '

    # STREAM CLASS INHERITANCE
    @upy_cmd_c_r()
    def read_data(self):
        return self.dev_dict

    # SOCKETS METHODS
    @upy_cmd_c_r_nb(debug=True)
    def connect_SOC(self, host, port):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def disconnect_SOC(self):
        return self.dev_dict

    def start_server(self):
        self.connect_SOC(self.soc.host, self.port)
        self.soc.start_SOC()

    def stop_server(self):
        self.disconnect_SOC()
        self.soc.conn.close()
        self.soc.serv_soc.close()

    def soc_recv_message(self):
        try:
            data = self.soc.conn.recv(self.data_length)
            data_unpack = struct.unpack(self.p_format*self.n_vars, data)
            self.d.output = data_unpack
            return data_unpack
        except Exception as e:
            return None

    def soc_recv_chunk_message(self):
        try:
            data = self.soc.conn.recv(self.chunk_buffer_data_length)
            data_unpack = struct.unpack(self.p_format*self.chunk_buffer_size,
                                        data)
            self.d.output = data_unpack
            return data_unpack
        except Exception as e:
            return None

    # JSON

    def soc_recv_chunk_message_json(self):
        try:
            data = b' '
            while data.decode() != '}':
                data = self.soc.conn.recv(1)
                self._json_buffer += data.decode()
            data = b' '
            data_unpack = json.loads(self._json_buffer)
            self._json_buffer = ' '
            return data_unpack
        except Exception as e:
            print(e)
            self._json_errors += 1
            return None

    def is_chunk(self, x):
        if len(x) > self.n_vars:
            return True
        else:
            return False

    # STREAM METHODS
    @upy_cmd_c_r_nb(rtn=False)
    def sample_send(self):
        return self.dev_dict

    def soc_read_data(self, timeout=0.2):  # ONE SHOT READ (+ LOG_OPTION)
        self.sample_send()
        time.sleep(timeout)
        return self.soc_recv_message()

    def shot_read(self, on_message, timeout=0.5, log=False, name_file=None,
                  tag=None, buffer=False):
        soc_data = self.soc_read_data(timeout=timeout)
        on_message(soc_data)
        if log:
            if name_file not in os.listdir(self.log_dir):
                self.lognow_shot(self.sens_mode, filename=name_file, debug=True,
                                 rtn=False)

                self.log_data_shot(name_file, soc_data, n_tag=tag)
            else:
                self.log_data_shot(name_file, soc_data, n_tag=tag)
        if buffer:
            self.log_data_shot_buff(soc_data, n_tag=tag)

    @upy_cmd_c_r_nb_in_callback(rtn=False)
    def start_send(self, sampling_callback, timeout=100, on_init=None):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def stop_send(self):
        return self.dev_dict

    # CONTINUOS STREAM (+ LOG_OPTION (FILE OR BUFFER)) +(TEST OPTION)
    def continuous_stream(self, on_message, timeout=100, init=True,
                          static=False, log=False, buffer=False,
                          on_init=None, test=False):
        if init:
            self.fq = 1/(timeout/1000)
            self.header['fq(hz)'] = self.fq
            self.start_send(
                sampling_callback=self.sample_send_call, timeout=timeout, on_init=on_init)

        if log:
                name_file = self.lognow(self.sens_mode)
        if test:
            t0 = time.time()
            buffer = True
        if not static:
            while True:
                try:
                    soc_data = self.soc_recv_message()
                    on_message(soc_data)
                    if log:
                        self.log_data(name_file, soc_data)
                    if buffer:
                        self.log_data_buff(soc_data)
                except KeyboardInterrupt:
                    if test:
                        self.time_test = abs(time.time()-t0)
                    self.stop_send()
                    print('\n')
                    self.soc.flush()
                    print('Done!')
                    break
        else:
            print(self.header_msg.format(self.sens_mode, self.header['UNIT'],
                                         self.fq))
            print('\n')
            print(('{:^15}'*len(self.header['VAR'])
                   ).format(*self.header['VAR']))
            while True:
                try:
                    soc_data = self.soc_recv_message()
                    on_message(soc_data)
                    if log:
                        self.log_data(name_file, soc_data)
                    if buffer:
                        self.log_data_buff(soc_data)
                except KeyboardInterrupt:
                    if test:
                        self.time_test = abs(time.time()-t0)
                    self.stop_send()
                    print('\n')
                    self.soc.flush()
                    print('Done!')
                    break

    def data_print(self, x):
        try:
            print(self.data_print_msg.format(*x, self.header['UNIT']))
        except Exception as e:
            pass

    def data_print_static(self, x):
        try:
            decode = dict(
                zip(self.header['VAR'], [format(val, '.4f') for val in x]))
            sys.stdout.write("\033[K")
            print(('{:^15}'*len(decode.values())
                   ).format(*decode.values()), end='\r')
            sys.stdout.flush()
        except Exception as e:
            pass

    def data_print_chunk_static(self, x):
        try:
            decode = dict(
                zip(self.header['VAR'], [format(val, '.4f') for val in x[0]]))
            sys.stdout.write("\033[K")
            print(('{:^15}'*len(decode.values())
                   ).format(*decode.values()), end='\r')
            sys.stdout.flush()
        except Exception as e:
            pass

    def data_print_chunk_static_json(self, x):
        try:
            decode = dict(
                zip(self.header['VAR'], [format(val, '.4f') for val in [x[key][0] for key in x.keys()]]))
            sys.stdout.write("\033[K")
            print(('{:^15}'*len(decode.values())
                   ).format(*decode.values()), end='\r')
            sys.stdout.flush()
        except Exception as e:
            pass

    def continuous_chunk_stream(self, timeout=100, init=True,
                               log=False, buffer=False, on_init=None,
                               test=False, static=False):
        if init:
            self.fq = 1/(timeout/1000)
            self.header['fq(hz)'] = self.fq
            self.start_send(
                sampling_callback=self.chunk_send_call, timeout=timeout, on_init=on_init)

        if log:
                name_file = self.lognow(self.sens_mode)
        if test:
            t0 = time.time()
            buffer = True
        if not static:
            while True:
                try:
                    soc_data = self.soc_recv_chunk_message()
                    if log:
                        self.log_data_chunk(name_file, soc_data)
                    if buffer:
                        self.log_data_chunk_buff(soc_data)
                except KeyboardInterrupt:
                    if test:
                        self.time_test = abs(time.time()-t0)
                    self.stop_send()
                    print('\n')
                    self.soc.flush()
                    print('Done!')
                    break
        else:
            print(self.header_msg.format(self.sens_mode, self.header['UNIT'],
                                         self.fq))
            print('\n')
            print(('{:^15}'*len(self.header['VAR'])
                   ).format(*self.header['VAR']))
            while True:
                try:
                    soc_data = self.soc_recv_chunk_message()
                    self.data_print_chunk_static(soc_data)
                    if log:
                        self.log_data_chunk(name_file, soc_data)
                    if buffer:
                        self.log_data_chunk_buff(soc_data)
                except KeyboardInterrupt:
                    if test:
                        self.time_test = abs(time.time()-t0)
                    self.stop_send()
                    print('\n')
                    self.soc.flush()
                    print('Done!')
                    break

    def continuous_chunk_stream_json(self, timeout=100, init=True,
                                    log=False, buffer=False, on_init=None,
                                    test=False, static=False):
        if init:
            self.fq = 1/(timeout/1000)
            self.header['fq(hz)'] = self.fq
            self.start_send(
                sampling_callback=self.chunk_send_json, timeout=timeout,
                on_init=on_init)

        if log:
                name_file = self.lognow(self.sens_mode)
        if test:
            t0 = time.time()
            buffer = True
        if not static:
            while True:
                try:
                    soc_data = self.soc_recv_chunk_message_json()
                    if log:
                        self.log_data_chunk_json(name_file, soc_data)
                    if buffer:
                        self.log_data_chunk_buff_json(soc_data)
                except KeyboardInterrupt:
                    if test:
                        self.time_test = abs(time.time()-t0)
                    self.stop_send()
                    print('\n')
                    self.soc.flush()
                    print('Done!')
                    break
        else:
            print(self.header_msg.format(self.sens_mode, self.header['UNIT'],
                                         self.fq))
            print('\n')
            print(('{:^15}'*len(self.header['VAR'])
                   ).format(*self.header['VAR']))
            while True:
                try:
                    soc_data = self.soc_recv_chunk_message_json()
                    self.data_print_chunk_static_json(soc_data)
                    if log:
                        self.log_data_chunk_json(name_file, soc_data)
                    if buffer:
                        self.log_data_chunk_buff_json(soc_data)
                except KeyboardInterrupt:
                    if test:
                        self.time_test = abs(time.time()-t0)
                    self.stop_send()
                    print('\n')
                    self.soc.flush()
                    print('Done!')
                    break

    # CALLBACKS

    def sample_send_call(self, x):
        pass

    def chunk_send_call(self, x):
        pass

    def chunk_send_json(self, x):
        pass

    # LOG methods

    # FILE LOG

    def lognow(self, sensor_mode, filename=None, debug=True, rtn=True):
        file_name = 'log_{}_{}.txt'.format(sensor_mode,
                                           datetime.now().strftime("%m_%d_%Y_%H_%M_%S"))
        if filename is not None:
            file_name = filename
        if debug:
            print('Saving file {} ...'.format(file_name))
        with open(file_name, 'w') as file_log:
            file_log.write(json.dumps(self.header))
            file_log.write('\n')
        if rtn:
            return file_name

    def log_data(self, filename, data):
        try:
            data_pack = dict(zip(self.header['VAR'],
                                 [val for val in data]))
            with open(filename, 'a') as file_log:
                file_log.write(json.dumps(data_pack))
                file_log.write('\n')
        except Exception as e:
            pass

    def lognow_shot(self, sensor_mode, filename=None, debug=True, rtn=True):
        file_name = filename
        if debug:
            print('Saving file {} ...'.format(file_name))
        with open(file_name, 'w') as file_log:
            header_vars = self.header['VAR'].copy()
            header_vars.append('TS')
            header_unit = self.header['UNIT']
            SHOT_HEADER = {'VAR': header_vars, 'UNIT': header_unit}
            file_log.write(json.dumps(SHOT_HEADER))
            file_log.write('\n')
        if rtn:
            return file_name

    def log_data_shot(self, filename, data, n_tag=None):
        try:
            data_pack = dict(zip(self.header['VAR']+['TS'],
                                 [val for val in data]+[datetime.now().strftime("%m_%d_%Y_%H_%M_%S")]))
            if n_tag is not None:
                data_pack = dict(zip(self.header['VAR']+['TS'],
                                     [val for val in data]+[n_tag]))
            with open(filename, 'a') as file_log:
                file_log.write(json.dumps(data_pack))
                file_log.write('\n')
        except Exception as e:
            pass

    def log_data_chunk(self, filename, data):
        try:
            data_pack = dict(zip(self.header['VAR'],
                                 [list(data)]))
            with open(filename, 'a') as file_log:
                file_log.write(json.dumps(data_pack))
                file_log.write('\n')
        except Exception as e:
            pass

    def log_data_chunk_json(self, filename, data):
        try:
            if data is not None:
                with open(filename, 'a') as file_log:
                    file_log.write(json.dumps(data))
                    file_log.write('\n')
        except Exception as e:
            pass

    # BUFFER LOG

    def log_data_buff(self, data):
        try:
            data_pack = dict(zip(self.header['VAR'],
                                 [val for val in data]))
            self.buffer.append(json.dumps(data_pack))
        except Exception as e:
            pass

    def log_data_shot_buff(self, data, n_tag=None):
        try:
            data_pack = dict(zip(self.header['VAR']+['TS'],
                                 [val for val in data]+[datetime.now().strftime("%m_%d_%Y_%H_%M_%S")]))
            if n_tag is not None:
                data_pack = dict(zip(self.header['VAR']+['TS'],
                                     [val for val in data]+[n_tag]))
            self.buffer.append(json.dumps(data_pack))
        except Exception as e:
            pass

    def log_data_chunk_buff(self, data):
        try:
            data_pack = dict(zip(self.header['VAR'],
                                 [list(data)]))
            self.buffer.append(json.dumps(data_pack))
        except Exception as e:
            pass

    def log_data_chunk_buff_json(self, data):
        try:
            if data is not None:
                self.buffer.append(json.dumps(data))
        except Exception as e:
            print(e)
            pass

    def read_buffer(self, flatten=False):
        list_of_vars = {var: [] for var in self.header['VAR']}
        for message in self.buffer:
            try:
                vals = json.loads(message)
                for key in vals.keys():
                    list_of_vars[key].append(vals[key])
            except Exception as e:
                pass
        if flatten:
            for key in vals.keys():
                list_of_vars[key] = [item for sublist in list_of_vars[key]
                                     for item in sublist]
        return (list_of_vars)

    def read_buffer_shot(self):
        list_of_vars = {var: [] for var in self.header['VAR']+['TS']}
        for message in self.buffer:
            try:
                vals = json.loads(message)
                for key in vals.keys():
                    list_of_vars[key].append(vals[key])
            except Exception as e:
                pass
        return (list_of_vars)

    def flush_buffer(self):
        self.buffer = []

    # STREAM TEST
    def get_stream_test(self, chunk=False, json=False):
        print('STREAM TEST RESULTS ARE:')
        print('TEST DURATION : {} (s)'.format(self.time_test))
        # # FIND SAMPLING RATE
        # Method 1:
        N_DATA_PACKETS = len(self.buffer)  # Number of batches received
        print('DATA PACKETS : {} packets'.format(N_DATA_PACKETS))
        # (assuming al batches = buffer_size long)
        BUFFERSIZE = self.chunk_buffer_size
        if not chunk:
            BUFFERSIZE = 1
        Fs = ((N_DATA_PACKETS+1)*BUFFERSIZE/self.time_test)
        print('SAMPLES PER PACKET : {}'.format(BUFFERSIZE))
        print('VARIABLES PER SAMPLE : {}; {}'.format(
            len(self.header['VAR']), self.header['VAR']))
        packet_size = self.chunk_buffer_data_length
        if not chunk:
            packet_size = self.data_length
        if json:
            packet_size = self.chunk_buffer_json_size
        print('SIZE OF PACKETS: {} bytes'.format(packet_size))
        print('Period: {} ms ; Fs:{} Hz, Data send rate: {} packets/s of {} samples'.format(
            round((1/Fs)*1e3), round(Fs, -1),
            round(N_DATA_PACKETS/self.time_test), BUFFERSIZE))
        kBs = round(N_DATA_PACKETS/self.time_test)*packet_size/1024
        print('DATA TRANSFER RATE (kBps): {} kB/s'.format(kBs))
        print('DATA TRANSFER RATE (Mbps): {} Mbps'.format((kBs*8)/1000))
#############################################
# SENSORS


# IMU LSM9DS1

class LSM9DS1:  # TODO: IMU_STREAMER + IMU_LOGGER
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


# WEATHER SENSOR BME280

class BME280:
    def __init__(self, device, name='bme'):
        """Phantom BME280 class"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}

    @upy_cmd_c_r()
    def read_compensated_data(self):
        return self.dev_dict


# ADC ADS1115
class ADS1115:
    def __init__(self, device, name='ads'):
        """Phantom ADS1115 class"""
        self.d = device
        self.name = name
        self.dev_dict = {'name': self.name, 'dev': device}

    @upy_cmd_c_r(rtn=False)
    def set_conv(self, rate=4, channel1=0, channel2=None):
        return self.dev_dict

    @upy_cmd_c_r()
    def raw_to_v(self, raw):
        return self.dev_dict

    @upy_cmd_c_r()
    def read(self, rate=4, channel1=0, channel2=None):
        return self.dev_dict

    @upy_cmd_c_r()
    def read_rev(self):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def alert_start(self, rate=4, channel1=0, channel2=None,
                    threshold_high=0x4000):
        return self.dev_dict

    @upy_cmd_c_r(rtn=False)
    def conversion_start(self, rate=4, channel1=0, channel2=None):
        return self.dev_dict

    @upy_cmd_c_r()
    def alert_read(self):
        return self.dev_dict

# POWER/CURRENT/VOLTAGE INA219


# IRQ SENSOR classes

# IMU (lsm9ds1)
class IMU_IRQ(IRQ_MG):
    def __init__(self, device, name, init_soc=False, port=8005, p_format='f',
                 n_vars=3, sensor=None, log_dir=None, logg=None):
        super().__init__(device, name, init_soc=init_soc, port=port,
                         p_format=p_format, n_vars=n_vars, sensor=None,
                         log_dir=log_dir, logg=logg)
        self.header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'g=-9.8m/s^2'}
        self.sens_mode = 'ACCELEROMETER'
        self.data_print_msg = "X: {}, Y: {}, Z: {} ({})"

    @upy_cmd_c_r()
    def set_mode(self, mode):
        return self.dev_dict

    def setup_mode(self, v_mode):
        if v_mode == 'acc':
            self.header['UNIT'] = 'g=-9.8m/s^2'
            self.sens_mode = 'ACCELEROMETER'
            self.set_mode(v_mode)
        if v_mode == 'gyro':
            self.header['UNIT'] = 'deg/s'
            self.sens_mode = 'GYROSCOPE'
            self.set_mode(v_mode)
        if v_mode == 'mag':
            self.header['UNIT'] = 'gauss'
            self.sens_mode = 'MAGNETOMETER'
            self.set_mode(v_mode)


# WEATHER (bme280)

class BME_IRQ(IRQ_MG):
    def __init__(self, device, name, init_soc=False, port=8005, p_format='f',
                 n_vars=3, sensor=None, log_dir=None, logg=None):
        super().__init__(device, name, init_soc=init_soc, port=port,
                         p_format=p_format, n_vars=n_vars, sensor=None,
                         log_dir=log_dir, logg=logg)
        # CUSTOM SENS
        self.header = {'VAR': ['Temp', 'Press', 'RH'], 'UNIT': 'C ; Pa ; %'}
        self.sens_mode = 'WEATHER'
        self.header_msg = 'Streaming BME {}: Temp, Press, Rel.Hum ({}),fq={}Hz'
        self.data_print_msg = "T: {}, P: {}, RH: {} ({})"


# ADC (ADS1115)

class ADS_IRQ(IRQ_MG):
    def __init__(self, device, name, init_soc=False, port=8005, p_format='f',
                 n_vars=1, sensor=None, log_dir=None, logg=None, channel=0):
        super().__init__(device, name, init_soc=init_soc, port=port,
                         p_format=p_format, n_vars=n_vars, sensor=None,
                         log_dir=log_dir, logg=logg)
        # CUSTOM SENS
        self.channel = channel
        self.header = {'VAR': ['V'], 'UNIT': 'Volts'}
        self.sens_mode = 'ADS CHANNEl {}'.format(self.channel)
        self.header_msg = 'Streaming {}: V ({}),fq={}Hz'
        self.data_print_msg = "V: {} ({})"

    @upy_cmd_c_r()
    def set_channel(self, channel):
        return self.dev_dict

    @upy_cmd_c_r()
    def set_mode(self, mode):
        return self.dev_dict

    @upy_cmd_c_r()
    def read_shot(self):
        return self.dev_dict

    @upy_cmd_c_r()
    def init_ads(self):
        return self.dev_dict

    def setup_channel(self, v_channel):
        self.set_channel(v_channel)
        self.channel = v_channel
        self.sens_mode = 'CHANNEl {}'.format(self.channel)
        self.init_ads()

        def init_ads_call(self):  # on_init callback
            pass
# STREAM SENSOR classes


# IMU (LSM9DS1)

class IMU_STREAMER(STREAMER):
    def __init__(self, device, name, init_soc=False, port=8005, p_format='f',
                 n_vars=3, log_dir=None, max_digit=8, chunk_buff_size=32,
                 soc_timeout=1):
        super().__init__(device, name, init_soc=init_soc, port=port,
                         p_format=p_format,
                         n_vars=n_vars, log_dir=log_dir,
                         chunk_buffer_size=chunk_buff_size,
                         soc_timeout=soc_timeout)
        # CUSTOM SENS
        self.header = {'VAR': ['X', 'Y', 'Z'], 'UNIT': 'g=-9.8m/s^2',
                       'fq(hz)': self.fq}
        self.sens_mode = 'ACCELEROMETER'
        self.header_msg = 'Streaming IMU {}: X, Y, Z ({}),fq={}Hz'
        self.data_print_msg = "X: {}, Y: {}, Z: {} ({})"
        self.max_dig = max_digit
        self.chunk_buffer_json_size = self.get_json_chunk_size()

    def get_json_chunk_size(self):
        json_size = ((self.max_dig+2)*self.chunk_buffer_size*self.n_vars)+(7*self.n_vars)
        return json_size

    @upy_cmd_c_r()
    def set_mode(self, mode):
        return self.dev_dict

    def setup_mode(self, v_mode):
        if v_mode == 'acc':
            self.header['UNIT'] = 'g=-9.8m/s^2'
            self.sens_mode = 'ACCELEROMETER'
            self.set_mode(v_mode)
        if v_mode == 'gyro':
            self.header['UNIT'] = 'deg/s'
            self.sens_mode = 'GYROSCOPE'
            self.set_mode(v_mode)
        if v_mode == 'mag':
            self.header['UNIT'] = 'gauss'
            self.sens_mode = 'MAGNETOMETER'
            self.set_mode(v_mode)

    # CALLBACK
    def chunk_send_json(self, x):
        pass


# BME280

class BME_STREAMER(STREAMER):
    def __init__(self, device, name, init_soc=False, port=8005, p_format='f',
                 n_vars=3, log_dir=None, soc_timeout=1, logg=None):
        super().__init__(device, name, init_soc=init_soc, port=port,
                         p_format=p_format,
                         n_vars=n_vars, log_dir=log_dir,
                         soc_timeout=soc_timeout, logg=logg)
        # CUSTOM SENS
        self.header = {'VAR': ['Temp', 'Press', 'RH'], 'UNIT': 'C ; Pa ; %',
                       'fq(hz)': self.fq}
        self.sens_mode = 'WEATHER'
        self.header_msg = 'Streaming BME {}: Temp, Press, Rel.Hum ({}),fq={}Hz'
        self.data_print_msg = "T: {}, P: {}, RH: {} ({})"


# ADS1115

class ADS_STREAMER(STREAMER):
    def __init__(self, device, name, init_soc=False, port=8005, p_format='f',
                 n_vars=1, log_dir=None, channel=0, soc_timeout=1):
        super().__init__(device, name, init_soc=init_soc, port=port,
                         p_format=p_format,
                         n_vars=n_vars, log_dir=log_dir,
                         soc_timeout=soc_timeout)

        # CUSTOM SENS
        self.channel = channel
        self.header = {'VAR': ['V'], 'UNIT': 'Volts',
                       'fq(hz)': self.fq}
        self.sens_mode = 'ADS CHANNEl {}'.format(self.channel)
        self.header_msg = 'Streaming {}: V ({}),fq={}Hz'
        self.data_print_msg = "V: {} ({})"

    @upy_cmd_c_r()
    def set_channel(self, channel):
        return self.dev_dict

    @upy_cmd_c_r()
    def set_mode(self, mode):
        return self.dev_dict

    @upy_cmd_c_r()
    def read_shot(self):
        return self.dev_dict

    @upy_cmd_c_r()
    def init_ads(self):
        return self.dev_dict

    def setup_channel(self, v_channel):
        self.set_channel(v_channel)
        self.channel = v_channel
        self.sens_mode = 'CHANNEl {}'.format(self.channel)
        self.init_ads()

    def init_ads_call(self):  # on_init callback
        pass

# POWER/CURRENT/VOLTAGE INA219

# UPYUTILS(OUTPUT : BUZZER, SERVO, STEPPER, DISPLAY)
#############################################
# U_LOGGER_SERVER (logging through sockets) then make a project with python logging

# SOCKETS UTILS PYTHON


# SOCKET SERVER

class socket_server:
    """
    Socket server simple class
    """

    def __init__(self, port, buff=1024, soc_timeout=1, logg=None):
        self.log = logg
        try:
            self.host = self.find_localip()
            if self.log is not None:
                self.log.info('Host IP: {}'.format(self.host))
            else:
                print(self.host)
        except Exception as e:
            if self.log is not None:
                self.log.error('Connection ERROR', exc_info=True)
            else:
                print(str(e))
            pass
        self.host_ap = '192.168.4.1'
        self.port = port
        self.serv_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = None
        self.buff = bytearray(buff)
        self.conn = None
        self.addr_client = None
        self.soc_timeout = soc_timeout

    def find_localip(self):
        ip_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_soc.connect(('8.8.8.8', 1))
        local_ip = ip_soc.getsockname()[0]
        ip_soc.close()
        return local_ip

    def start_SOC(self):
        self.serv_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_soc.bind((self.host, self.port))
        self.serv_soc.listen(1)
        if self.log is not None:
            self.log.info('Server listening...')
        else:
            print('Server listening...')
        self.conn, self.addr_client = self.serv_soc.accept()
        if self.log is not None:
            self.log.info(('Connection received from: {}:{}'.format(*self.addr_client)))
        else:
            print('Connection received from: {}:{}'.format(*self.addr_client))
        self.conn.settimeout(self.soc_timeout)

    def start_SOC_AP(self):
        self.serv_soc.bind((self.host_ap, self.port))
        self.serv_soc.listen(1)
        if self.log is not None:
            self.log.info('Server listening...')
        else:
            print('Server listening...')
        self.conn, self.addr_client = self.serv_soc.accept()
        if self.log is not None:
            self.log.info(('Connection received from: {}:{}'.format(*self.addr_client)))
        else:
            print('Connection received from: {}:{}'.format(*self.addr_client))
        self.conn.settimeout(self.soc_timeout)

    def flush(self):
        flushed = 0
        while flushed == 0:
            try:
                self.serv_soc.recv(128)
            except Exception as e:
                flushed = 1
                # print('flushed!')
        flushed = 0
        while flushed == 0:
            try:
                self.conn.recv(128)
            except Exception as e:
                flushed = 1
                if self.log is not None:
                    self.log.info('Flushed!')
                else:
                    print('Flushed!')

    def send_message(self, message):
        self.conn.sendall(bytes(message, 'utf-8'))

    def recv_message(self):
        self.buff[:] = self.conn.recv(len(self.buff))
        print(self.buff.decode())


# SOCKET CLIENT

class socket_client:
    """
    Socket client simple class
    """

    def __init__(self, host, port, buff=1024, soc_timeout=1):
        self.cli_soc = None
        self.host = host
        self.port = port
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        self.buff = bytearray(buff)
        self.soc_timeout = soc_timeout

    def connect_SOC(self):
        self.cli_soc.connect(self.addr)
        self.cli_soc.settimeout(self.soc_timeout)

    def flush(self):
        flushed = 0
        while flushed == 0:
            try:
                self.cli_soc.recv(128)
            except Exception as e:
                flushed = 1
                print('flushed!')

    def send_message(self, message):
        self.cli_soc.sendall(bytes(message, 'utf-8'))

    def recv_message(self):
        self.buff[:] = self.cli_soc.recv(len(self.buff))
        print(self.buff.decode())

# MICROPYTHON
# U_SERVER_SOCKET
# U_SERVER_CLIENT
