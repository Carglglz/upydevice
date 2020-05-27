#!/usr/bin/env python

import asyncio
import struct
from bleak import BleakClient
from bleak import discover
from upydevice.chars import ble_char_dict
import time
import ast
from array import array
import sys


def ble_scan(log=False):
    devs = []

    async def run():
        devices = await discover()
        for d in devices:
            if log:
                print(d)
            devs.append(d)
        return devs

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run())

# MACOS


NUS = {"6E400001-B5A3-F393-E0A9-E50E24DCCA9E": "Nordic UART Service",
       "6E400003-B5A3-F393-E0A9-E50E24DCCA9E": 'TX',
       "6E400002-B5A3-F393-E0A9-E50E24DCCA9E": 'RX'}

# Linux # if sys.platform linux :
if sys.platform == 'linux':
    NUS = {"6e400001-b5a3-f393-e0a9-e50e24dcca9e": "Nordic UART Service",
           "6e400003-b5a3-f393-e0a9-e50e24dcca9e": 'TX',
           "6e400002-b5a3-f393-e0a9-e50e24dcca9e": 'RX'}


# class BASE_SBLE_DEVICE:
#     def __init__(self, scan_dev, init=False):
#         # BLE
#         self.ble_client = None
#         self.UUID = scan_dev.address
#         self.name = scan_dev.name
#         self.rssi = scan_dev.rssi
#         self.connected = False
#         self.services = {}
#         self.readables = {}
#         self.writeables = {}
#         self.loop = asyncio.get_event_loop()
#         #
#         self.bytes_sent = 0
#         self.buff = b''
#         self.raw_buff = b''
#         self.prompt = b'>>> '
#         self.response = ''
#         self._kbi = '\x03'
#         self._banner = '\x02'
#         self._reset = '\x04'
#         self._traceback = b'Traceback (most recent call last):'
#         self._flush = b''
#         self.output = None
#         self.platform = None
#         #
#         if init:
#             self.connect()
#             # do connect
#
#     async def connect_client(self, n_tries=3):
#         n = 0
#         self.ble_client = BleakClient(self.UUID, loop=self.loop)
#         while n < n_tries:
#             try:
#                 await self.ble_client.connect()
#                 self.connected = await self.ble_client.is_connected()
#                 if self.connected:
#                     print("Connected to: {}".format(self.UUID))
#                     break
#             except Exception as e:
#                 print(e)
#                 print('Trying again...')
#                 time.sleep(1)
#                 n += 1
#
#     async def disconnect_client(self):
#         await self.ble_client.disconnect()
#         self.connected = await self.ble_client.is_connected()
#         if not self.connected:
#             print("Disconnected succesfully")
#
#     def connect(self, n_tries=3):
#         self.loop.run_until_complete(self.connect_client(n_tries=n_tries))
#
#     def disconnect(self):
#         self.loop.run_until_complete(self.disconnect_client())
#
#     # SERVICES
#     def get_services(self, log=True):
#         for service in self.ble_client.services:
#             if service.description == 'Unknown' or service.uuid in list(NUS.keys()):
#                 is_NUS = True
#                 if log:
#                     print("[Service] {0}: {1}".format(
#                         service.uuid, NUS[service.uuid]))
#                 self.services[NUS[service.uuid]] = {
#                     'UUID': service.uuid, 'CHARS': {}}
#             else:
#                 is_NUS = False
#                 if log:
#                     print("[Service] {0}: {1}".format(
#                         service.uuid, service.description))
#                 self.services[service.description] = {
#                     'UUID': service.uuid, 'CHARS': {}}
#
#             for char in service.characteristics:
#                 if is_NUS:
#                     if "read" in char.properties:
#                         self.readables[NUS[char.uuid]] = char.uuid
#                     if "write" in char.properties:
#                         self.writeables[NUS[char.uuid]] = char.uuid
#                     self.services[NUS[service.uuid]]['CHARS'][char.uuid] = {char.description: ",".join(
#                         char.properties), 'Descriptors': {descriptor.uuid: descriptor.handle for descriptor in char.descriptors}}
#                 else:
#                     if "read" in char.properties:
#                         self.readables[service.description] = char.uuid
#                     if "write" in char.properties:
#                         self.writeables[service.description] = char.uuid
#
#                     self.services[service.description]['CHARS'][char.uuid] = {char.description: ",".join(
#                         char.properties), 'Descriptors': {descriptor.uuid: descriptor.handle for descriptor in char.descriptors}}
#                 if log:
#                     if is_NUS:
#                         print("\t[Characteristic] {0}: ({1}) | Name: {2}".format(
#                             char.uuid, ",".join(
#                                 char.properties), NUS[char.uuid]))
#                     else:
#                         print("\t[Characteristic] {0}: ({1}) | Name: {2}".format(
#                             char.uuid, ",".join(
#                                 char.properties), ble_char_dict[char.uuid]))
#
#                 if log:
#                     for descriptor in char.descriptors:
#                         print(
#                             "\t\t[Descriptor] {0}: (Handle: {1}) ".format(
#                                 descriptor.uuid, descriptor.handle
#                             )
#                         )
#
#     async def as_read_service(self, uuid):
#         return bytes(await self.ble_client.read_gatt_char(uuid))
#
#     def read_service_raw(self, key=None, uuid=None):
#         if key is not None:
#             if key in list(self.readables.keys()):
#                 data = self.loop.run_until_complete(
#                     self.as_read_service(self.readables[key]))
#                 return data
#             else:
#                 print('Service not readable')
#
#         else:
#             if uuid is not None:
#                 if uuid in list(self.readables.values()):
#                     data = self.loop.run_until_complete(
#                         self.as_read_service(uuid))
#                     return data
#                 else:
#                     print('Service not readable')
#
#     def read_service(self, key=None, uuid=None, data_fmt="<h"):
#         try:
#             return struct.unpack(data_fmt, self.read_service_raw(key=key, uuid=uuid))
#         except Exception as e:
#             print(e)
#
#     async def as_write_service(self, uuid, data):
#         await self.ble_client.write_gatt_char(uuid, data)
#
#     def write_service_raw(self, key=None, uuid=None, data=None):
#         if key is not None:
#             if key in list(self.writeables.keys()):
#                 data = self.loop.run_until_complete(
#                     self.as_write_service(self.writeables[key], bytes(data)))
#                 return data
#             else:
#                 print('Service not writeable')
#
#         else:
#             if uuid is not None:
#                 if uuid in list(self.writeables.values()):
#                     data = self.loop.run_until_complete(
#                         self.as_write_service(uuid, bytes(data)))
#                     return data
#                 else:
#                     print('Service not writeable')
#
#     def write(self, cmd):
#         data = bytes(cmd, 'utf-8')
#         n_bytes = len(data)
#         self.write_service_raw(key='RX', data=data)
#         return n_bytes
#
#     def read_all(self):
#         try:
#             self.raw_buff = b''
#             while self.prompt not in self.raw_buff:
#                 data = self.read_service_raw(key='TX')
#                 self.raw_buff += data
#
#             return self.raw_buff
#         except Exception as e:
#             print(e)
#             return self.raw_buff
#
#     def flush(self):
#         flushed = 0
#         self.buff = self.read_all()
#         flushed += 1
#         self.buff = b''
#
#     def wr_cmd(self, cmd, silent=False, rtn=True, rtn_resp=False,
#                long_string=False):
#         self.output = None
#         self.response = ''
#         self.buff = b''
#         self.flush()
#         self.bytes_sent = self.write(cmd+'\r')
#         # time.sleep(0.1)
#         # self.buff = self.read_all()[self.bytes_sent:]
#         self.buff = self.read_all()
#         if self.buff == b'':
#             # time.sleep(0.1)
#             self.buff = self.read_all()
#         # print(self.buff)
#         # filter command
#         cmd_filt = bytes(cmd + '\r\n', 'utf-8')
#         self.buff = self.buff.replace(cmd_filt, b'', 1)
#         if self._traceback in self.buff:
#             long_string = True
#         if long_string:
#             self.response = self.buff.replace(b'\r', b'').replace(
#                 b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
#         else:
#             self.response = self.buff.replace(b'\r\n', b'').replace(
#                 b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
#         if not silent:
#             if self.response != '\n' and self.response != '':
#                 print(self.response)
#             else:
#                 self.response = ''
#         if rtn:
#             self.get_output()
#             if self.output == '\n' and self.output == '':
#                 self.output = None
#             if self.output is None:
#                 if self.response != '' and self.response != '\n':
#                     self.output = self.response
#         if rtn_resp:
#             return self.output
#
#     def kbi(self, silent=True, pipe=None):
#         if pipe is not None:
#             self.wr_cmd(self._kbi, silent=silent)
#             bf_output = self.response.split('Traceback')[0]
#             traceback = 'Traceback' + self.response.split('Traceback')[1]
#             if bf_output != '' and bf_output != '\n':
#                 pipe(bf_output)
#             pipe(traceback, std='stderr')
#         else:
#             self.wr_cmd(self._kbi, silent=silent)
#
#     def banner(self, pipe=None):
#         self.wr_cmd(self._banner, silent=True, long_string=True)
#         if pipe is None:
#             print(self.response.replace('\n\n', '\n'))
#         else:
#             pipe(self.response.replace('\n\n', '\n'))
#
#     def get_output(self):
#         try:
#             self.output = ast.literal_eval(self.response)
#         except Exception as e:
#             if 'bytearray' in self.response:
#                 try:
#                     self.output = bytearray(ast.literal_eval(
#                         self.response.strip().split('bytearray')[1]))
#                 except Exception as e:
#                     pass
#             else:
#                 if 'array' in self.response:
#                     try:
#                         arr = ast.literal_eval(
#                             self.response.strip().split('array')[1])
#                         self.output = array(arr[0], arr[1])
#                     except Exception as e:
#                         pass
#             pass


class BASE_BLE_DEVICE:
    def __init__(self, scan_dev, init=False, name=None, lenbuff=100):
        # BLE
        self.ble_client = None
        if hasattr(scan_dev, 'address'):
            self.UUID = scan_dev.address
            self.name = scan_dev.name
            self.rssi = scan_dev.rssi
        else:
            self.UUID = scan_dev
            self.name = name
        self.connected = False
        self.services = {}
        self.readables = {}
        self.writeables = {}
        self.loop = asyncio.get_event_loop()
        self.raw_buff_queue = asyncio.Queue()
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
        self._traceback = b'Traceback (most recent call last):'
        self._flush = b''
        self.output = None
        self.platform = None
        #
        if init:
            self.connect()
            # do connect

    async def connect_client(self, n_tries=3, log=True):
        n = 0
        self.ble_client = BleakClient(self.UUID, loop=self.loop)
        while n < n_tries:
            try:
                await self.ble_client.connect()
                self.connected = await self.ble_client.is_connected()
                if self.connected:
                    if log:
                        print("Connected to: {}".format(self.UUID))
                    break
            except Exception as e:
                if log:
                    print(e)
                    print('Trying again...')
                time.sleep(1)
                n += 1

    async def disconnect_client(self, log=True):
        await self.ble_client.disconnect()
        self.connected = await self.ble_client.is_connected()
        if not self.connected:
            if log:
                print("Disconnected succesfully")

    def connect(self, n_tries=3, show_servs=False, log=True):
        self.loop.run_until_complete(self.connect_client(n_tries=n_tries,
                                                         log=log))
        self.get_services(log=show_servs)

    def disconnect(self, log=True):
        self.loop.run_until_complete(self.disconnect_client(log=log))

    # SERVICES
    def get_services(self, log=True):
        for service in self.ble_client.services:
            if service.description == 'Unknown' or service.uuid in list(NUS.keys()):
                is_NUS = True
                if log:
                    print("[Service] {0}: {1}".format(
                        service.uuid, NUS[service.uuid]))
                self.services[NUS[service.uuid]] = {
                    'UUID': service.uuid, 'CHARS': {}}
            else:
                is_NUS = False
                if log:
                    print("[Service] {0}: {1}".format(
                        service.uuid, service.description))
                self.services[service.description] = {
                    'UUID': service.uuid, 'CHARS': {}}

            for char in service.characteristics:
                if is_NUS:
                    if "read" in char.properties or "notify" in char.properties:
                        self.readables[NUS[char.uuid]] = char.uuid
                    if "write" in char.properties:
                        self.writeables[NUS[char.uuid]] = char.uuid
                    self.services[NUS[service.uuid]]['CHARS'][char.uuid] = {char.description: ",".join(
                        char.properties), 'Descriptors': {descriptor.uuid: descriptor.handle for descriptor in char.descriptors}}
                else:
                    if "read" in char.properties:
                        self.readables[service.description] = char.uuid
                    if "write" in char.properties:
                        self.writeables[service.description] = char.uuid

                    self.services[service.description]['CHARS'][char.uuid] = {char.description: ",".join(
                        char.properties), 'Descriptors': {descriptor.uuid: descriptor.handle for descriptor in char.descriptors}}
                if log:
                    if is_NUS:
                        print("\t[Characteristic] {0}: ({1}) | Name: {2}".format(
                            char.uuid, ",".join(
                                char.properties), NUS[char.uuid]))
                    else:
                        try:
                            print("\t[Characteristic] {0}: ({1}) | Name: {2}".format(
                                char.uuid, ",".join(
                                    char.properties), ble_char_dict[char.uuid]))
                        except Exception as e:
                            print("\t[Characteristic] {0}: ({1}) | Name: {2}".format(
                                char.uuid, ",".join(
                                    char.properties), char.description))

                if log:
                    for descriptor in char.descriptors:
                        print(
                            "\t\t[Descriptor] {0}: (Handle: {1}) ".format(
                                descriptor.uuid, descriptor.handle
                            )
                        )

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

    async def as_read_service(self, uuid):
        return bytes(await self.ble_client.read_gatt_char(uuid))

    def read_service_raw(self, key=None, uuid=None):
        if key is not None:
            if key in list(self.readables.keys()):
                data = self.loop.run_until_complete(
                    self.as_read_service(self.readables[key]))
                return data
            else:
                print('Service not readable')

        else:
            if uuid is not None:
                if uuid in list(self.readables.values()):
                    data = self.loop.run_until_complete(
                        self.as_read_service(uuid))
                    return data
                else:
                    print('Service not readable')

    def read_service(self, key=None, uuid=None, data_fmt="<h"):
        try:
            return struct.unpack(data_fmt, self.read_service_raw(key=key, uuid=uuid))
        except Exception as e:
            print(e)

    async def as_write_service(self, uuid, data):
        await self.ble_client.write_gatt_char(uuid, data)

    def write_service_raw(self, key=None, uuid=None, data=None):
        if key is not None:
            if key in list(self.writeables.keys()):
                data = self.loop.run_until_complete(
                    self.as_write_service(self.writeables[key], self.fmt_data(data, CR=False))) # make fmt_data
                return data
            else:
                print('Service not writeable')

        else:
            if uuid is not None:
                if uuid in list(self.writeables.values()):
                    data = self.loop.run_until_complete(
                        self.as_write_service(uuid, self.fmt_data(data, CR=False))) # make fmt_data
                    return data
                else:
                    print('Service not writeable')

    def read_callback(self, sender, data):
        self.raw_buff += data

    def read_callback_follow(self, sender, data):
        try:
            if not self._cmdfiltered:
                cmd_filt = bytes(self._cmdstr + '\r\n', 'utf-8')
                data = b'' + data
                data = data.replace(cmd_filt, b'', 1)
                # data = data.replace(b'\r\n>>> ', b'')
                self._cmdfiltered = True
            else:
                try:
                    data = b'' + data
                    # data = data.replace(b'\r\n>>> ', b'')
                except Exception as e:
                    pass
            self.raw_buff += data
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
        await self.ble_client.start_notify(self.readables['TX'], self.read_callback)
        if len(data) > self.len_buffer:
            for i in range(0, len(data), self.len_buffer):
                await self.ble_client.write_gatt_char(self.writeables['RX'], data[i:i+self.len_buffer])

        else:
            await self.ble_client.write_gatt_char(self.writeables['RX'], data)
        while self.prompt not in self.raw_buff:
            await asyncio.sleep(0.01, loop=self.loop)
        await self.ble_client.stop_notify(self.readables['TX'])
        if rtn_buff:
            return self.raw_buff

    async def as_write_read_follow(self, data, rtn_buff=False):
        if not self.is_notifying:
            try:
                await self.ble_client.start_notify(self.readables['TX'], self.read_callback_follow)
                self.is_notifying = True
            except Exception as e:
                pass
        if len(data) > self.len_buffer:
            for i in range(0, len(data), self.len_buffer):
                await self.ble_client.write_gatt_char(self.writeables['RX'], data[i:i+self.len_buffer])
        else:
            await self.ble_client.write_gatt_char(self.writeables['RX'], data)
        while self.prompt not in self.raw_buff:
            try:
                await asyncio.sleep(0.01, loop=self.loop)
            except KeyboardInterrupt:
                print('Catch here1')
                data = bytes(self._kbi, 'utf-8')
                await self.ble_client.write_gatt_char(self.writeables['RX'], data)
        if self.is_notifying:
            try:
                await self.ble_client.stop_notify(self.readables['TX'])
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
        self.write_service_raw(key='RX', data=data)
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

    def wr_cmd(self, cmd, silent=False, rtn=True, rtn_resp=False,
               long_string=False, follow=False, kb=False):
        self.output = None
        self.response = ''
        self.raw_buff = b''
        self.buff = b''
        self._cmdstr = cmd
        # self.flush()
        self.bytes_sent = self.send_recv_cmd(cmd, follow=follow, kb=kb) # make fmt_datas
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
        data = self.fmt_data(cmd) # make fmt_data
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
            await self.ble_client.write_gatt_char(self.writeables['RX'], data)

    def banner(self, pipe=None, kb=False, follow=False):
        self.wr_cmd(self._banner, silent=True, long_string=True,
                    kb=kb, follow=follow)
        if pipe is None and not follow:
            print(self.response.replace('\n\n', '\n'))
        else:
            if pipe:
                pipe(self.response.replace('\n\n', '\n'))

    def reset(self, silent=False):
        if not silent:
            print('Rebooting device...')
        self.write_service_raw(key='RX', data=self._reset)
        if not silent:
            print('Done!')

    async def as_reset(self, silent=False):
        if not silent:
            print('Rebooting device...')
        await self.as_write_service(self.writeables['RX'], bytes(self._reset, 'utf-8'))
        if not silent:
            print('Done!')
        return None

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
    def __init__(self, scan_dev, init=False, name=None, lenbuff=100):
        super().__init__(scan_dev, init=init, name=name, lenbuff=lenbuff)
