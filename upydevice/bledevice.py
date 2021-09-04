#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2020 Carlos Gil Gonzalez
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# import logging
#
# logging.getLogger(
#     "bleak.backends.corebluetooth.CentralManagerDelegate").setLevel(logging.ERROR)
# logging.getLogger('asyncio').setLevel(logging.WARNING)

import asyncio
import struct
from datetime import datetime
from bleak import BleakClient
from bleak import BleakScanner
from bleak_sigspec.utils import get_char_value, get_xml_char
import uuid as U_uuid
import time
import ast
from array import array
import sys
import traceback
import multiprocessing
from binascii import hexlify
from .exceptions import DeviceException, DeviceNotFound
from unsync import unsync


_WASPDEVS = ['P8', 'PineTime', 'Pixl.js']


def ble_scan(log=False):
    devs = []

    async def run():
        devices = await BleakScanner.discover()
        for d in devices:
            if log:
                print(d)
            devs.append(d)
        return devs

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run())


class BASE_BLE_DEVICE:
    def __init__(self, scan_dev, init=False, name=None, lenbuff=100,
                 rssi=None, conn_debug=None):
        # BLE
        self.ble_client = None
        if hasattr(scan_dev, 'address'):
            self.UUID = scan_dev.address
            self.name = scan_dev.name
            self.rssi = scan_dev.rssi
            self.address = self.UUID
        else:
            self.UUID = scan_dev
            self.name = name
            self.rssi = rssi
            self.address = self.UUID
        self.connected = False
        self.services = {}
        self.services_rsum = {}
        self.services_rsum_handles = {}
        self.chars_desc_rsum = {}
        self.readables = {}
        self.writeables = {}
        self.notifiables = {}
        self.readables_handles = {}
        self.writeables_handles = {}
        self.notifiables_handles = {}
        self.loop = asyncio.get_event_loop()
        # self.raw_buff_queue = asyncio.Queue()
        self.kb_cmd = None
        self.is_notifying = False
        self.cmd_finished = True
        self.len_buffer = lenbuff
        #
        self.bytes_sent = 0
        self.buff = b''
        self.raw_buff = b''
        self.prompt = b'>>> '
        self.response = ''
        self._cmdstr = ''
        self._cmdfiltered = False
        self._kbi = '\x03'
        self._banner = '\x02'
        self._reset = '\x04'
        self._hreset = "import machine; machine.reset()\r"
        self._traceback = b'Traceback (most recent call last):'
        self._flush = b''
        self.output = None
        self.platform = None
        self.break_flag = None
        self.log = conn_debug
        #
        if init:
            self.connect(debug=self.log)
            if self.name in _WASPDEVS:
                self.len_buffer = 20
            # do connect

    def set_event_loop(self, loop):
        self.loop = loop
        # self.ble_client.loop = loop

    async def connect_client(self, n_tries=3, debug=False):
        n = 0
        self.ble_client = BleakClient(self.UUID)
        while n < n_tries:
            try:
                await asyncio.wait_for(self.ble_client.connect(timeout=3),
                                       timeout=60)
                self.connected = self.ble_client.is_connected
                if self.connected:
                    try:
                        if hasattr(self.ble_client._peripheral, 'name'):
                            if callable(self.ble_client._peripheral.name):
                                self.name = self.ble_client._peripheral.name()
                        else:
                            self.name = self.ble_client._device_info.get('Name')
                        if hasattr(self.ble_client, 'mtu_size'):
                            pass
                            # self.len_buffer = self.ble_client.mtu_size - 3
                    except Exception as e:
                        pass
                    if self.log or debug:
                        print("Connected to: {}".format(self.UUID))
                    break
            except Exception as e:
                if debug:
                    if not self.break_flag:
                        print(e)
                        print('Trying again...')
                    else:
                        break
                time.sleep(1)
                n += 1

    async def disconnect_client(self, log=True, timeout=None):
        if timeout:

            await asyncio.wait_for(self.ble_client.disconnect(),
                                   timeout=timeout)

        else:
            await self.ble_client.disconnect()
        self.connected = self.ble_client.is_connected
        if not self.connected:
            if self.log or log:
                print("Disconnected successfully")

    def connect(self, n_tries=5, show_servs=False, debug=False):
        self.loop.run_until_complete(self.connect_client(n_tries=n_tries,
                                                         debug=debug))
        if self.connected:
            self.get_services(log=show_servs)
        else:
            raise DeviceNotFound('BleDevice @ {} is not reachable'.format(self.UUID))

    def is_connected(self):
        self.connected = self.ble_client.is_connected
        return self.connected

    def disconnect(self, log=False, timeout=None):
        if self.connected:
            self.loop.run_until_complete(self.disconnect_client(log=log,
                                                                timeout=timeout))

    def set_disconnected_callback(self, callback):
        self.ble_client.set_disconnected_callback(callback)

    def disconnection_callback(self, client):
        self.connected = False

    # RSSI
    def get_RSSI(self):
        if hasattr(self.ble_client, 'get_rssi'):
            self.rssi = self.loop.run_until_complete(self.ble_client.get_rssi())
        else:
            self.rssi = 0
        return self.rssi
    # SERVICES

    def get_services(self, log=True):
        for service in self.ble_client.services:
            if service.description == 'Nordic UART Service':
                is_NUS = True
                if log:
                    print("[Service] {0}: {1}".format(
                        service.uuid.lower(), service.description))
                self.services[service.description] = {
                    'UUID': service.uuid.lower(), 'CHARS': {}}
            else:
                is_NUS = False
                if log:
                    print("[Service] {0}: {1}".format(
                        service.uuid.lower(), service.description))
                self.services[service.description] = {
                    'UUID': service.uuid.lower(), 'CHARS': {}}
                self.services_rsum_handles[service.description] = []

            for char in service.characteristics:
                if is_NUS:
                    if "read" in char.properties or "notify" in char.properties:
                        self.readables[char.description] = char.uuid
                    if "write" in char.properties:
                        self.writeables[char.description] = char.uuid
                    try:
                        self.services[service.description]['CHARS'][char.uuid] = {char.description: ",".join(
                            char.properties), 'Descriptors': {descriptor.uuid: descriptor.handle for descriptor in char.descriptors}}
                    except Exception as e:

                        self.services[service.description]['CHARS'][char.uuid] = {char.description: ",".join(
                            char.properties), 'Descriptors': {descriptor.uuid: descriptor.handle for descriptor in char.descriptors}}
                else:
                    self.services_rsum_handles[service.description].append(char.handle)
                    if "read" in char.properties:
                        try:
                            self.readables[char.description] = char.uuid
                            self.readables_handles[char.handle] = char.description
                        except Exception as e:
                            print(e)

                    if "notify" in char.properties or 'indicate' in char.properties:
                        try:
                            self.notifiables[char.description] = char.uuid
                            self.notifiables_handles[char.handle] = char.description
                        except Exception as e:
                            print(e)

                    if "write" in char.properties or 'write-without-response' in char.properties:
                        try:
                            self.writeables[char.description] = char.uuid
                            self.writeables_handles[char.handle] = char.description
                        except Exception as e:
                            print(e)
                    try:
                        self.services[service.description]['CHARS'][char.uuid] = {char.description: ",".join(
                            char.properties), 'Descriptors': {descriptor.uuid: descriptor.handle for descriptor in char.descriptors}}
                    except Exception as e:
                        print(e)

                    self.chars_desc_rsum[char.description] = {}
                    for descriptor in char.descriptors:
                        self.chars_desc_rsum[char.description][descriptor.description] = descriptor.handle
                if log:
                    if is_NUS:
                        print("\t[Characteristic] {0}: ({1}) | Name: {2}".format(
                            char.uuid, ",".join(
                                char.properties), char.description))
                    else:
                        try:
                            print("\t[Characteristic] {0}: ({1}) | Name: {2}".format(
                                char.uuid, ",".join(
                                    char.properties), char.description))
                        except Exception as e:
                            print(e)

                if log:
                    for descriptor in char.descriptors:
                        print(
                            "\t\t[Descriptor] [{0}]: {1} (Handle: {2}) ".format(
                                descriptor.uuid,
                                descriptor.description,
                                descriptor.handle
                            )
                        )
        self.services_rsum = {key: [list(list(val['CHARS'].values())[i].keys())[0] for i in range(
            len(list(val['CHARS'].values())))] for key, val in self.services.items()}
    # WRITE/READ SERVICES

    def fmt_data(self, data, CR=True):
        if sys.platform == 'linux':
            if CR:
                return bytearray(data+'\r', 'utf-8')
            else:
                return bytearray(data, 'utf-8')
        else:
            if CR:
                return bytes(data+'\r', 'utf-8')
            else:
                return bytes(data, 'utf-8')

    async def as_read_descriptor(self, handle):
        return bytes(await self.ble_client.read_gatt_descriptor(handle))

    def read_descriptor_raw(self, key=None, char=None):
        if key is not None:
            # print(self.chars_desc_rsum[char])
            if key in list(self.chars_desc_rsum[char]):
                data = self.loop.run_until_complete(
                    self.as_read_descriptor(self.chars_desc_rsum[char][key]))
                return data
            else:
                print('Descriptor not available for this characteristic')

    def read_descriptor(self, key=None, char=None, data_fmt="utf8"):
        try:
            if data_fmt == 'utf8':
                data = self.read_descriptor_raw(key=key, char=char).decode('utf8')
                return data
            else:
                data, = struct.unpack(data_fmt, self.read_char_raw(key=key, char=char))
                return data
        except Exception as e:
            print(e)

    async def as_read_char(self, uuid):
        return bytes(await self.ble_client.read_gatt_char(uuid))

    def read_char_raw(self, key=None, uuid=None, handle=None):
        if key is not None:
            if key in list(self.readables.keys()):
                if handle:
                    data = self.loop.run_until_complete(
                        self.as_read_char(handle))
                else:
                    data = self.loop.run_until_complete(
                        self.as_read_char(self.readables[key]))
                return data
            else:
                print('Characteristic not readable')

        else:
            if uuid is not None:
                if uuid in list(self.readables.values()):
                    if handle:
                        data = self.loop.run_until_complete(
                            self.as_read_char(handle))
                    else:
                        data = self.loop.run_until_complete(
                            self.as_read_char(uuid))
                    return data
                else:
                    print('Characteristic not readable')

    def read_char(self, key=None, uuid=None, data_fmt="<h", handle=None):
        try:
            if data_fmt == 'utf8':  # Here function that handles format and unpack properly
                data = self.read_char_raw(
                    key=key, uuid=uuid, handle=handle).decode('utf8')
                return data
            else:
                if data_fmt == 'raw':
                    data = self.read_char_raw(key=key, uuid=uuid, handle=handle)
                    return data
                else:
                    data, = struct.unpack(data_fmt, self.read_char_raw(key=key,
                                                                       uuid=uuid,
                                                                       handle=handle))
                return data
        except Exception as e:
            print(e)

    async def as_write_char(self, uuid, data):
        await self.ble_client.write_gatt_char(uuid, data)

    def write_char(self, key=None, uuid=None, data=None, handle=None):
        if key is not None:
            if key in list(self.writeables.keys()):
                if handle:
                    data = self.loop.run_until_complete(
                        self.as_write_char(handle, data))
                else:
                    data = self.loop.run_until_complete(
                        self.as_write_char(self.writeables[key], data))  # make fmt_data
                return data
            else:
                print('Characteristic not writeable')

        else:
            if uuid is not None:
                if uuid in list(self.writeables.values()):
                    if handle:
                        data = self.loop.run_until_complete(
                            self.as_write_char(handle, data))
                    else:
                        data = self.loop.run_until_complete(
                            self.as_write_char(uuid, data))  # make fmt_data
                    return data
                else:
                    print('Characteristic not writeable')

    def write_char_raw(self, key=None, uuid=None, data=None):
        if key is not None:
            if key in list(self.writeables.keys()):
                data = self.loop.run_until_complete(
                    self.as_write_char(self.writeables[key], self.fmt_data(data, CR=False)))  # make fmt_data
                return data
            else:
                print('Characteristic not writeable')

        else:
            if uuid is not None:
                if uuid in list(self.writeables.values()):
                    data = self.loop.run_until_complete(
                        self.as_write_char(uuid, self.fmt_data(data, CR=False)))  # make fmt_data
                    return data
                else:
                    print('Characteristic not writeable')

    def read_callback(self, sender, data):
        self.raw_buff += data

    def read_callback_follow(self, sender, data):
        try:
            cmd_filt = bytes(self._cmdstr + '\r\n', 'utf-8')
            self.raw_buff += data
            if not cmd_filt in self.raw_buff:
                pass
            else:
                if cmd_filt == self.raw_buff:
                   data = b''
                if not self._cmdfiltered:
                    cmd_filt = bytes(self._cmdstr + '\r\n', 'utf-8')
                    data = b'' + data
                    if cmd_filt in data:
                        data = data.replace(cmd_filt, b'', 1)
                        # data = data.replace(b'\r\n>>> ', b'')
                        self._cmdfiltered = True
                else:
                    try:
                        data = b'' + data
                        # data = data.replace(b'\r\n>>> ', b'')
                    except Exception as e:
                        pass
                # self.raw_buff += data
                # self._line_buff += data + b'-'
                if self.prompt in data:
                    data = data.replace(b'\r', b'').replace(b'\r\n>>> ', b'').replace(
                        b'>>> ', b'').decode('utf-8', 'ignore')
                    if data != '':
                        print(data, end='')
                else:
                    data = data.replace(b'\r', b'').replace(b'\r\n>>> ', b'').replace(
                        b'>>> ', b'').decode('utf-8', 'ignore')
                    print(data, end='')
        except KeyboardInterrupt:
            print('CALLBACK_KBI')
            pass
        #

    async def as_write_read_waitp(self, data, rtn_buff=False):
        await self.ble_client.start_notify(self.readables['Nordic UART TX'], self.read_callback)
        if len(data) > self.len_buffer:
            for i in range(0, len(data), self.len_buffer):
                await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data[i:i+self.len_buffer])
                await asyncio.sleep(0.1, loop=self.loop)

        else:
            await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data)
        while self.prompt not in self.raw_buff:
            await asyncio.sleep(0, loop=self.loop)
        await self.ble_client.stop_notify(self.readables['Nordic UART TX'])
        if rtn_buff:
            return self.raw_buff

    async def as_write_read_follow(self, data, rtn_buff=False):
        if not self.is_notifying:
            try:
                await self.ble_client.start_notify(self.readables['Nordic UART TX'], self.read_callback_follow)
                self.is_notifying = True
            except Exception as e:
                pass
        if len(data) > self.len_buffer:
            for i in range(0, len(data), self.len_buffer):
                await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data[i:i+self.len_buffer])
        else:
            await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data)
        while self.prompt not in self.raw_buff:
            try:
                await asyncio.sleep(0, loop=self.loop)
            except KeyboardInterrupt:
                print('Catch here1')
                data = bytes(self._kbi, 'utf-8')
                await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data)
        if self.is_notifying:
            try:
                await self.ble_client.stop_notify(self.readables['Nordic UART TX'])
                self.is_notifying = False
            except Exception as e:
                pass
        self._cmdfiltered = False
        if rtn_buff:
            return self.raw_buff

    def write_read(self, data='', follow=False, kb=False):
        if not follow:
            if not kb:
                try:
                    self.loop.run_until_complete(
                        self.as_write_read_waitp(data))
                except Exception as e:
                    print(e)
            else:
                asyncio.ensure_future(
                    self.as_write_read_waitp(data), loop=self.loop)
                # wait here until there is raw_buff

        else:
            if not kb:
                try:
                    self.loop.run_until_complete(
                        self.as_write_read_follow(data))
                except Exception as e:
                    print('Catch here0')
                    print(e)
            else:

                asyncio.ensure_future(self.as_write_read_follow(
                    data, rtn_buff=True), loop=self.loop)

    def send_recv_cmd(self, cmd, follow=False, kb=False):
        data = self.fmt_data(cmd)  # make fmt_data
        n_bytes = len(data)
        self.write_read(data=data, follow=follow, kb=kb)
        return n_bytes

    def write(self, cmd):
        data = self.fmt_data(cmd, CR=False)  # make fmt_data
        n_bytes = len(data)
        self.write_char_raw(key='Nordic UART RX', data=cmd)
        return n_bytes

    def read_all(self):
        try:
            return self.raw_buff
        except Exception as e:
            print(e)
            return self.raw_buff

    def flush(self):
        flushed = 0
        self.buff = self.read_all()
        flushed += 1
        self.buff = b''

    def cmd(self, *args, **kargs):
        return self.wr_cmd(*args, **kargs)

    def wr_cmd(self, cmd, silent=False, rtn=True, long_string=False,
               rtn_resp=False, follow=False, pipe=None, multiline=False,
               dlog=False, nb_queue=None, kb=False):
        self.output = None
        self.response = ''
        self.raw_buff = b''
        self.buff = b''
        self._cmdstr = cmd
        # self.flush()
        self.bytes_sent = self.send_recv_cmd(
            cmd, follow=follow, kb=kb)  # make fmt_datas
        # time.sleep(0.1)
        # self.buff = self.read_all()[self.bytes_sent:]
        self.buff = self.read_all()
        if self.buff == b'':
            # time.sleep(0.1)
            self.buff = self.read_all()
        # print(self.buff)
        # filter command
        if follow:
            silent = True
        cmd_filt = bytes(cmd + '\r\n', 'utf-8')
        self.buff = self.buff.replace(cmd_filt, b'', 1)
        if self._traceback in self.buff:
            long_string = True
        if long_string:
            self.response = self.buff.replace(b'\r', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        else:
            self.response = self.buff.replace(b'\r\n', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        if not silent:
            if self.response != '\n' and self.response != '':
                try:
                    if self._traceback.decode() in self.response:
                        raise DeviceException(self.response)
                    else:
                        print(self.response)
                except Exception as e:
                    print(e)
                    self.response = ''
            else:
                self.response = ''
        if rtn:
            self.get_output()
            if self.output == '\n' and self.output == '':
                self.output = None
            if self.output is None:
                if self.response != '' and self.response != '\n':
                    self.output = self.response
            if nb_queue is not None:
                nb_queue.put((self.output), block=False)
        if rtn_resp:
            return self.output

    async def as_wr_cmd(self, cmd, silent=False, rtn=True, rtn_resp=False,
                        long_string=False, follow=False, kb=False):
        self.output = None
        self.response = ''
        self.raw_buff = b''
        self.buff = b''
        self._cmdstr = cmd
        self.cmd_finished = False
        # self.flush()
        data = self.fmt_data(cmd)  # make fmt_data
        n_bytes = len(data)
        self.bytes_sent = n_bytes
        # time.sleep(0.1)
        # self.buff = self.read_all()[self.bytes_sent:]
        if follow:
            self.buff = await self.as_write_read_follow(data, rtn_buff=True)
        else:
            self.buff = await self.as_write_read_waitp(data, rtn_buff=True)
        if self.buff == b'':
            # time.sleep(0.1)
            self.buff = self.read_all()
        # print(self.buff)
        # filter command
        if follow:
            silent = True
        cmd_filt = bytes(cmd + '\r\n', 'utf-8')
        self.buff = self.buff.replace(cmd_filt, b'', 1)
        if self._traceback in self.buff:
            long_string = True
        if long_string:
            self.response = self.buff.replace(b'\r', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        else:
            self.response = self.buff.replace(b'\r\n', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        if not silent:
            if self.response != '\n' and self.response != '':
                print(self.response)
            else:
                self.response = ''
        if rtn:
            self.get_output()
            if self.output == '\n' and self.output == '':
                self.output = None
            if self.output is None:
                if self.response != '' and self.response != '\n':
                    self.output = self.response
        self.cmd_finished = True
        if rtn_resp:
            return self.output

    def kbi(self, silent=True, pipe=None):
        if pipe is not None:
            self.wr_cmd(self._kbi, silent=silent)
            bf_output = self.response.split('Traceback')[0]
            traceback = 'Traceback' + self.response.split('Traceback')[1]
            if bf_output != '' and bf_output != '\n':
                pipe(bf_output)
            pipe(traceback, std='stderr')
        else:
            self.wr_cmd(self._kbi, silent=silent)

    async def as_kbi(self):
        for i in range(1):
            print('This is buff: {}'.format(self.raw_buff))
            await asyncio.sleep(1, loop=self.loop)
            data = bytes(self._kbi + '\r', 'utf-8')
            await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data)

    def banner(self, pipe=None, kb=False, follow=False):
        self.wr_cmd(self._banner, silent=True, long_string=True,
                    kb=kb, follow=follow)
        if pipe is None and not follow:
            print(self.response.replace('\n\n', '\n'))
        else:
            if pipe:
                pipe(self.response.replace('\n\n', '\n'))

    def reset(self, silent=False, reconnect=True, hr=False):
        if not silent:
            print('Rebooting device...')
        if not hr:
            self.write_char_raw(key='Nordic UART RX', data=self._reset)
        else:
            self.write_char_raw(key='Nordic UART RX', data=self._hreset)

        self.connected = self.is_connected()
        if reconnect:
            time.sleep(2)
            self.connect(n_tries=10, debug=self.log)
        if not silent:
            print('Done!')

    async def as_reset(self, silent=True):
        if not silent:
            print('Rebooting device...')
        await self.as_write_char(self.writeables['Nordic UART RX'], bytes(self._reset, 'utf-8'))
        if not silent:
            print('Done!')
        return None

    def cmd_nb(self, command, silent=False, rtn=True, long_string=False,
               rtn_resp=False, follow=False, pipe=None, multiline=False,
               dlog=False, block_dev=True):
        if block_dev:
            pass  # Not possible in multiprocessing
            # self.dev_process_raw = multiprocessing.Process(
            #     target=self.wr_cmd, args=(command, silent, rtn, long_string, rtn_resp,
            #                               follow, pipe, multiline, dlog,
            #                               self.output_queue))
            # self.dev_process_raw.start()
        else:
            self.bytes_sent = self.write(command+'\r')

    def get_output(self):
        try:
            self.output = ast.literal_eval(self.response)
        except Exception as e:
            if 'bytearray' in self.response:
                try:
                    self.output = bytearray(ast.literal_eval(
                        self.response.strip().split('bytearray')[1]))
                except Exception as e:
                    pass
            else:
                if 'array' in self.response:
                    try:
                        arr = ast.literal_eval(
                            self.response.strip().split('array')[1])
                        self.output = array(arr[0], arr[1])
                    except Exception as e:
                        pass
            pass


class BLE_DEVICE(BASE_BLE_DEVICE):
    def __init__(self, scan_dev, init=False, name=None, lenbuff=100,
                 rssi=None, conn_debug=False, autodetect=False):
        super().__init__(scan_dev, init=init, name=name, lenbuff=lenbuff,
                         rssi=rssi, conn_debug=conn_debug)
        self.dev_class = 'BleDevice'
        self.appearance = 0
        self.appearance_tag = 'UNKNOWN'
        self.manufacturer = 'UNKNOWN'
        self.model_number = 'UNKNOWN'
        self.firmware_rev = 'UNKNOWN'
        self._devinfoserv = 'Device Information'
        self.MAC_addrs = ''
        self.device_info = {}
        self.chars_xml = {}
        self.dev_platform = ''
        self.read_char_metadata()
        self.get_appearance()
        self.get_MAC_addrs()
        self.get_MANUFACTURER()
        self.get_MODEL_NUMBER()
        self.get_FIRMWARE_REV()
        self.get_SERIAL_NUMBER()
        self.get_HARDWARE_REV()
        self.get_SOFTWARE_REV()
        self.batt_power_state = {'Charging': 'Unknown', 'Discharging': 'Unknown',
                                 'Level': 'Unknown', 'Present': 'Unknown'}
        self.get_batt_power_state()
        if autodetect:
            if not init:
                self.connect(debug=self.log)
            if self.connected:
                repr_cmd = 'import gc;import os; [os.uname().sysname, os.uname().release, os.uname().version, os.uname().machine]'
                (self.dev_platform, self._release,
                 self._version, self._machine) = self.cmd(repr_cmd,
                                                          silent=True,
                                                          rtn_resp=True)

    def __repr__(self):
        if self.connected and 'Nordic UART RX' in self.writeables:
            repr_cmd = 'import sys;import os;from machine import unique_id;' +\
                '[os.uname().sysname, os.uname().release, os.uname().version,' +\
                'os.uname().machine, unique_id(), sys.implementation.name]'
            (self.dev_platform, self._release,
             self._version, self._machine, muuid, imp) = self.cmd(repr_cmd,
                                                                  silent=True,
                                                                  rtn_resp=True)
            vals = hexlify(muuid).decode()
            imp = imp[0].upper() + imp[1:]
            imp = imp.replace('p', 'P')
            self._mac = ':'.join([vals[i:i+2] for i in range(0, len(vals), 2)])
            fw_str = '{} {}; {}'.format(imp, self._version, self._machine)
            return 'BleDevice @ {}, Type: {} , Class: {}\nFirmware: {}\n(MAC: {}, Local Name: {}, RSSI: {} dBm)'.format(self.UUID,
                                                                                                                        self.dev_platform,
                                                                                                                        self.dev_class,
                                                                                                                        fw_str,
                                                                                                                        self._mac,
                                                                                                                        self.name,
                                                                                                                        self.get_RSSI())
        elif not self.connected:
            return 'BleDevice @ {}, (Disconnected)'.format(self.UUID)
        else:
            return 'BleDevice @ {}, Local Name: {}, RSSI: {} dBm'.format(self.UUID,
                                                                         self.name,
                                                                         self.get_RSSI())

    def is_reachable(self):
        return self.is_connected()  # Fix if disconnected

    def read_char_metadata(self):
        for serv in self.services_rsum.keys():
            for char in self.services_rsum[serv]:
                if char in list(self.readables.keys()) + list(self.writeables.keys()) + list(self.notifiables.keys()):
                    try:
                        self.chars_xml[char] = get_xml_char(char)
                    except Exception as e:
                        pass

    def get_char_value(self, char, rtn_flags=False, debug=False, handle=None):
        raw_val = self.read_char(char, data_fmt="raw", handle=handle)
        f_value = get_char_value(raw_val, self.chars_xml[char],
                                 rtn_flags=rtn_flags,
                                 debug=debug)
        return f_value

    def pformat_field_value(self, field_data, field='', sep=',', prnt=True,
                            rtn=False, timestamp=False):

        if not timestamp:
            try:
                field_string_values = ["{} {}".format(
                    field_data['Value'], field_data['Symbol'])]
            except Exception as e:
                if 'RR-Interval' in field_data:
                    field_interval_data = field_data['RR-Interval']
                    field_string_values = ['{} {}'.format(field_interval_data[interval]['Value'],
                                                          field_interval_data[interval]['Symbol']) for interval in field_interval_data]
                else:
                    field_string_values = ["{}".format(field_data['Value'])]
            if field:
                if prnt:
                    print('{}: {}'.format(field, sep.join(field_string_values)))
                elif rtn:
                    return '{}: {}'.format(field, sep.join(field_string_values))
            else:
                if prnt:
                    print(sep.join(field_string_values))
                elif rtn:
                    return sep.join(field_string_values)
        else:
            field_values = []
            for dt in field_data:
                if field_data[dt]['Unit'] == 'month':
                    dtm = datetime.strptime(field_data[dt]['Value'], '%B')
                    val = dtm.month
                else:
                    val = field_data[dt]['Value']
                field_values.append(val)
            try:
                date_string = datetime.strftime(
                    datetime(*field_values), "%Y-%m-%d %H:%M:%S")
                if prnt:
                    print(date_string)
                elif rtn:
                    return date_string
            except Exception as e:
                print(e)
                return None

    def pformat_char_value(self, data, char='', only_val=False, one_line=False,
                           sep=',', custom=None, symbols=True, prnt=True,
                           rtn=False):
        if not custom:
            if not one_line:
                if char:
                    print('{}:'.format(char))
                if not only_val:
                    for key in data:
                        try:
                            print('{}: {} {}'.format(
                                key, data[key]['Value'], data[key]['Symbol']))
                        except Exception as e:
                            print('{}: {} '.format(key, data[key]['Value']))
                else:
                    for key in data:
                        try:
                            print('{} {}'.format(
                                data[key]['Value'], data[key]['Symbol']))
                        except Exception as e:
                            print('{}'.format(data[key]['Value']))
            else:

                if not only_val:
                    try:
                        char_string_values = ["{}: {} {}".format(
                            key, data[key]['Value'], data[key]['Symbol']) for key in data]
                    except Exception as e:
                        char_string_values = ["{}: {}".format(
                            key, data[key]['Value']) for key in data]
                    if char:
                        if prnt:
                            print('{}: {}'.format(char, sep.join(char_string_values)))
                        elif rtn:
                            return '{}: {}'.format(char, sep.join(char_string_values))
                    else:
                        if prnt:
                            print(sep.join(char_string_values))
                        elif rtn:
                            return sep.join(char_string_values)
                else:
                    try:
                        char_string_values = ["{} {}".format(
                            data[key]['Value'], data[key]['Symbol']) for key in data]
                    except Exception as e:
                        char_string_values = ["{}".format(
                            data[key]['Value']) for key in data]
                    if char:
                        if prnt:
                            print('{}: {}'.format(char, sep.join(char_string_values)))
                        elif rtn:
                            return '{}: {}'.format(char, sep.join(char_string_values))
                    else:
                        if prnt:
                            print(sep.join(char_string_values))
                        elif rtn:
                            return sep.join(char_string_values)
        else:
            if not symbols:
                print(custom.format(*[data[k]['Value'] for k in data]))
            else:
                print(custom.format(
                    *['{} {}'.format(data[k]['Value'], data[k]['Symbol']) for k in data]))

    def map_char_value(self, data, keys=[], string_fmt=False, one_line=True, sep=', '):
        if keys:
            if not string_fmt:
                return dict(zip(keys, data.values()))
            else:
                map_values = dict(zip(keys, data.values()))
                if one_line:
                    return sep.join([f"{k}: {v}" for k, v in map_values.items()])
                else:
                    sep += '\n'
                    return sep.join([f"{k}: {v}" for k, v in map_values.items()])

    def dict_char_value(self, data, raw=False):
        try:
            if raw:
                values = {k: {'Value': data[k]['Value'],
                              'Symbol': data[k]['Symbol']} for k in data}
            else:
                values = {k: '{} {}'.format(
                    data[k]['Value'], data[k]['Symbol']) for k in data}
        except Exception as e:
            values = {}
            if raw:
                for k in data:
                    if 'Symbol' in data[k]:
                        values[k] = {'Value': data[k]['Value'],
                                     'Symbol': data[k]['Symbol']}
                    else:
                        values[k] = {'Value': data[k]['Value']}
            else:
                for k in data:
                    if 'Symbol' in data[k]:
                        values[k] = '{} {}'.format(data[k]['Value'], data[k]['Symbol'])
                    else:
                        values[k] = data[k]['Value']
        return values

    def pformat_char_flags(self, data, sep='\n', prnt=False, rtn=True):
        try:
            char_string_values = [
                ["{}: {}".format(k, v) for k, v in data[key].items()] for key in data]
            all_values = []
            for values in char_string_values:
                if prnt:
                    print(sep.join(values))
                elif rtn:
                    all_values.append(sep.join(values))
            if rtn:
                return sep.join(all_values)

        except Exception as e:
            print(e)

    def get_appearance(self):
        APPR = 'Appearance'
        if self._devinfoserv in self.services.keys():
            if APPR in self.readables.keys():
                try:
                    appearance_info = self.get_char_value(APPR)
                    self.appearance = appearance_info['Category']['Value']
                    self.appearance_tag = '_'.join(
                        [tag.upper().replace(':', '') for tag in self.appearance.split()])
                    self.device_info[APPR] = self.appearance
                except Exception as e:
                    print(traceback.format_exc())
                    # pass
        else:
            self.appearance = 'UNKNOWN'
            self.device_info[APPR] = self.appearance

    def get_MAC_addrs(self):
        if '-' in self.UUID:
            byteaddr = U_uuid.UUID(self.UUID)
            hexaddr = hex(sum([val for val in struct.unpack(
                "I"*4, byteaddr.bytes)])).replace('0', '', 1)
            MAC_addr = 'uu:'+':'.join([hexaddr[i:i+2]
                                       for i in range(0, len(hexaddr), 2)])
            self.MAC_addrs = MAC_addr
        else:
            self.MAC_addrs = self.UUID

    def get_MANUFACTURER(self):
        MNS = 'Manufacturer Name String'
        if self._devinfoserv in self.services.keys():
            if MNS in self.readables.keys():
                try:
                    man_string = self.read_char(
                        key=MNS, data_fmt=self.chars_xml[MNS].fields['Manufacturer Name']['Ctype'])
                    self.manufacturer = man_string
                    self.device_info[MNS] = self.manufacturer
                except Exception as e:
                    self.device_info[MNS] = self.manufacturer
                    print(e)
        else:
            self.device_info[MNS] = self.manufacturer

    def get_MODEL_NUMBER(self):
        MNS = 'Model Number String'
        if self._devinfoserv in self.services.keys():
            MNS = 'Model Number String'
            if MNS in self.chars_xml.keys():
                try:
                    model_string = self.read_char(
                        key=MNS, data_fmt=self.chars_xml[MNS].fields['Model Number']['Ctype'])
                    self.model_number = model_string
                    self.device_info[MNS] = self.model_number
                except Exception as e:
                    self.device_info[MNS] = self.model_number
                    print(e)
        else:
            self.device_info[MNS] = self.model_number

    def get_FIRMWARE_REV(self):
        FMW = 'Firmware Revision String'
        if self._devinfoserv in self.services.keys():
            if FMW in self.chars_xml.keys():
                try:
                    firmware_string = self.read_char(
                        key=FMW, data_fmt=self.chars_xml[FMW].fields['Firmware Revision']['Ctype'])
                    self.firmware_rev = firmware_string
                    self.device_info[FMW] = self.firmware_rev
                except Exception as e:
                    self.device_info[FMW] = self.firmware_rev
                    print(e)
        else:
            self.device_info[FMW] = self.firmware_rev

    def get_SERIAL_NUMBER(self):
        SNS = 'Serial Number String'
        if self._devinfoserv in self.services.keys():
            if SNS in self.chars_xml.keys():
                try:
                    serial_string = self.read_char(
                        key=SNS, data_fmt=self.chars_xml[SNS].fields['Serial Number']['Ctype'])
                    self.device_info[SNS] = serial_string
                except Exception as e:
                    print(e)

    def get_HARDWARE_REV(self):
        HRS = 'Hardware Revision String'
        if self._devinfoserv in self.services.keys():
            if HRS in self.chars_xml.keys():
                try:
                    hardware_string = self.read_char(
                        key=HRS, data_fmt=self.chars_xml[HRS].fields['Hardware Revision']['Ctype'])
                    self.device_info[HRS] = hardware_string
                except Exception as e:
                    print(e)

    def get_SOFTWARE_REV(self):
        SRS = 'Software Revision String'
        if self._devinfoserv in self.services.keys():
            if SRS in self.chars_xml.keys():
                try:
                    software_string = self.read_char(
                        key=SRS, data_fmt=self.chars_xml[SRS].fields['Software Revision']['Ctype'])
                    self.device_info[SRS] = software_string
                except Exception as e:
                    print(e)

    def get_SYSTEM_ID(self):
        SID = 'System ID'
        if self._devinfoserv in self.services.keys():
            if SID in self.chars_xml.keys():
                try:
                    sys_id = self.get_char_value(SID)
                    self.device_info[SID] = '{}-{}'.format(*[val['Value']
                                                             for val in list(sys_id.values())])
                except Exception as e:
                    print(e)

    def unpack_batt_power_state(self):
        pow_skeys = self.get_char_value('Battery Power State')
        self.batt_power_state = self.map_powstate(pow_skeys['State']['Value'])

    def map_powstate(self, bp_state_dict):
        return dict(zip(['Battery Power Information',
                         'Discharging State',
                         'Charging State', 'Level'], bp_state_dict.values()))

    def get_batt_power_state(self):
        BPS = "Battery Power State"
        if 'Battery Service' in self.services.keys():
            if BPS in self.readables.keys():
                self.unpack_batt_power_state()

        else:
            pass

    def get_plain_format(self, field):
        """Iterates until the last level where Value is"""
        val = ""
        for k in field:
            if 'Value' in field[k]:
                try:
                    val += "{}: {} {} ; ".format(k,
                                                 field[k]['Value'],  field[k]['Symbol'])
                except Exception as e:
                    val += "{}: {} ; ".format(k, field[k]['Value'])
            else:
                val += self.get_plain_format(field[k])
        if val != "":
            return val

    def pformat_ref_char_value(self, char_value, rtn=False):
        for field in char_value:
            if 'Value' in char_value[field]:
                if not rtn:
                    print(field, char_value[field]['Value'])
                else:
                    return '{} {}'.format(field, char_value[field]['Value'])
            else:
                # iterate function
                val = self.get_plain_format(char_value[field])
                if not rtn:
                    print("{}: {}".format(field, val))
                else:
                    return "{}: {}".format(field, val)


class BleDevice(BLE_DEVICE):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)


class AsyncBleDevice(BLE_DEVICE):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        # self.loop = asyncio.new_event_loop()
        self.pipe = None
        self.pipe_mode = "stdout"  # "stderr"
        # std="stdout"

    @unsync
    async def as_connect(self, n_tries=5, show_servs=False, debug=False):
        await self.connect_client(n_tries=n_tries, debug=debug)
        if self.connected:
            self.get_services(log=True)
            if hasattr(self.ble_client._peripheral, 'name'):
                if callable(self.ble_client._peripheral.name):
                    self.name = self.ble_client._peripheral.name()
            else:
                self.name = self.ble_client._device_info.get('Name')
            if self.name in _WASPDEVS:
                self.len_buffer = 20
        else:
            raise DeviceNotFound('BleDevice @ {} is not reachable'.format(self.UUID))

    def connect(self, **kargs):
        return self.as_connect(**kargs).result()

    @unsync
    async def as_disconnect(self, log=False, timeout=None):
        if self.connected:
            await self.disconnect_client(log=log, timeout=timeout)

    def disconnect(self, **kargs):
        return self.as_disconnect(**kargs).result()

    @unsync
    async def un_wr_cmd(self, cmd, **kargs):
        output = await self.as_wr_cmd(cmd, **kargs)
        return output

    def wr_cmd(self, cmd, **kargs):
        return self.un_wr_cmd(cmd, **kargs).result()

    def banner(self, pipe=None, kb=False, follow=False):
        self.wr_cmd(self._banner, silent=True, long_string=True,
                    kb=kb, follow=follow)
        if pipe is None and not follow:
            print(self.response.replace('\n\n', '\n'))
        else:
            if pipe:
                pipe(self.response.replace('\n\n', '\n'))

    async def as_paste_buff(self, cmd, **kargs):
        # print('Here')
        long_command = cmd
        await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], b'\x05')
        await asyncio.sleep(1)
        # await self.dev.ble_client.write_gatt_char(self.dev.writeables['Nordic UART RX'], b'\x04')
        # print(long_command)
        lines = long_command.split('\n')
        # print(lines)
        for line in lines:
            self.flush()
            await asyncio.sleep(0.2)
            data = bytes(line + '\n', 'utf-8')
            if len(data) > self.len_buffer:
                for i in range(0, len(data), self.len_buffer):
                    await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data[i:i+self.len_buffer])
            else:
                await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data)
            if line == lines[-1]:
                self._cmdstr = line
        # print(self._cmdstr)
        # output = await self.as_wr_cmd('\x04', **kargs)

        # return output

    @unsync
    async def un_paste_buff(self, cmd, **kargs):
        await self.as_paste_buff(cmd, **kargs)

    def paste_buff(self, cmd, **kargs):
        return self.un_paste_buff(cmd, **kargs).result()

    # TODO: use a different callback pipe compatible

    def read_callback_follow(self, sender, data):
        try:
            cmd_filt = bytes(self._cmdstr + '\r\n', 'utf-8')
            self.raw_buff += data
            # self.pipe(data)
            # if not cmd_filt in self.raw_buff:
            #     pass
            # else:
            if not self._cmdfiltered:
                cmd_filt = bytes(self._cmdstr + '\r\n', 'utf-8')
                cmd_filt_pipe = bytes(self._cmdstr + '\n', 'utf-8')
                data = b'' + data
                if cmd_filt in data:
                    data = data.replace(cmd_filt, b'', 1)
                    # data = data.replace(b'\r\n>>> ', b'')
                    self._cmdfiltered = True
                if cmd_filt_pipe in data:
                    data = data.replace(cmd_filt_pipe, b'', 1)
                    self._cmdfiltered = True
            else:
                try:
                    data = b'' + data
                    # data = data.replace(b'\r\n>>> ', b'')
                except Exception as e:
                    pass
            # self.raw_buff += data
            # self._line_buff += data + b'-'
            if self.prompt in data:
                data = data.replace(b'\r', b'').replace(b'\r\n>>> ', b'').replace(
                    b'>>> ', b'').decode('utf-8', 'ignore')
                if data != '':
                    if not self.pipe:
                        print(data, end='')
                    else:
                        self.pipe(data, std=self.pipe_mode)
            else:
                data = data.replace(b'\r', b'').replace(b'\r\n>>> ', b'').replace(
                    b'>>> ', b'').decode('utf-8', 'ignore')
                if not self.pipe:
                    print(data, end='')
                else:
                    self.pipe(data, std=self.pipe_mode)
        except KeyboardInterrupt:
            print('CALLBACK_KBI')
            pass

    async def as_write_read_waitp(self, data, rtn_buff=False):
        await self.ble_client.start_notify(self.readables['Nordic UART TX'], self.read_callback)
        if len(data) > self.len_buffer:
            for i in range(0, len(data), self.len_buffer):
                await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data[i:i+self.len_buffer])
                await asyncio.sleep(0.1)

        else:
            await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data)
        while self.prompt not in self.raw_buff:
            await asyncio.sleep(0)
        await self.ble_client.stop_notify(self.readables['Nordic UART TX'])
        if rtn_buff:
            return self.raw_buff

    async def as_write_read_follow(self, data, rtn_buff=False):
        if not self.is_notifying:
            try:
                await self.ble_client.start_notify(self.readables['Nordic UART TX'], self.read_callback_follow)
                self.is_notifying = True
            except Exception as e:
                pass
        if len(data) > self.len_buffer:
            for i in range(0, len(data), self.len_buffer):
                await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data[i:i+self.len_buffer])
        else:
            await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data)
        while self.prompt not in self.raw_buff:
            try:
                await asyncio.sleep(0)
            except KeyboardInterrupt:
                print('Catch here1')
                data = bytes(self._kbi, 'utf-8')
                await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data)
        if self.is_notifying:
            try:
                await self.ble_client.stop_notify(self.readables['Nordic UART TX'])
                self.is_notifying = False
            except Exception as e:
                pass
        self._cmdfiltered = False
        if rtn_buff:
            return self.raw_buff

    async def as_wr_cmd(self, cmd, silent=False, rtn=True, rtn_resp=False,
                        long_string=False, follow=False, pipe=None, multiline=False,
                        dlog=False, kb=False):
        self.output = None
        self.response = ''
        self.raw_buff = b''
        self.buff = b''
        if cmd != self._reset:
            self._cmdstr = cmd
        self.cmd_finished = False
        self.pipe = pipe
        # self.flush()
        data = self.fmt_data(cmd)  # make fmt_data
        n_bytes = len(data)
        self.bytes_sent = n_bytes
        # time.sleep(0.1)
        # self.buff = self.read_all()[self.bytes_sent:]
        if follow:
            self.buff = await self.as_write_read_follow(data, rtn_buff=True)
        else:
            self.buff = await self.as_write_read_waitp(data, rtn_buff=True)
        if self.buff == b'':
            # time.sleep(0.1)
            self.buff = self.read_all()
        # print(self.buff)
        # filter command
        if follow:
            silent = True
        cmd_filt = bytes(cmd + '\r\n', 'utf-8')
        self.buff = self.buff.replace(cmd_filt, b'', 1)
        if self._traceback in self.buff:
            long_string = True
        if long_string:
            self.response = self.buff.replace(b'\r', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        else:
            self.response = self.buff.replace(b'\r\n', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
        if not silent:
            if self.response != '\n' and self.response != '':
                print(self.response)
            else:
                self.response = ''
        if rtn:
            self.get_output()
            if self.output == '\n' and self.output == '':
                self.output = None
            if self.output is None:
                if self.response != '' and self.response != '\n':
                    self.output = self.response
        self.cmd_finished = True
        if rtn_resp:
            return self.output

    # KBI

    async def as_kbi(self, silent=True, pipe=None):
        data = bytes(self._kbi + '\r', 'utf-8')
        self.pipe_mode = "stderr"
        await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data)
        while not self.cmd_finished:
            await asyncio.sleep(0)
        self.pipe_mode = "stdout"

    @unsync
    async def un_kbi(self, **kargs):
        await self.as_kbi(**kargs)

    def kbi(self, **kargs):
        return self.un_kbi(**kargs).result()

    # async def as_kbi(self, silent=True, pipe=None):
    #     data = bytes(self._kbi + '\r', 'utf-8')
    #     await self.ble_client.write_gatt_char(self.writeables['Nordic UART RX'], data)
    #     # if pipe is not None:
    #     #     self.wr_cmd(self._kbi, silent=silent, follow=True)
    #     #     bf_output = self.response.split('Traceback')[0]
    #     #     traceback = 'Traceback' + self.response.split('Traceback')[1]
    #     #     if bf_output != '' and bf_output != '\n':
    #     #         pipe(bf_output)
    #     #     pipe(traceback, std='stderr')
    #     # else:
    #     #     self.wr_cmd(self._kbi, silent=silent, follow=True)

    # RSSI
    @unsync
    async def as_get_RSSI(self):
        if hasattr(self.ble_client, 'get_rssi'):
            self.rssi = await self.ble_client.get_rssi()
        else:
            self.rssi = 0
        return self.rssi

    def get_RSSI(self):
        return self.as_get_RSSI().result()
