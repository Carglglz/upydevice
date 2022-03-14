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

import ast
import time
import socket
import multiprocessing
import shlex
import subprocess
from array import array
import netifaces
import nmap
import sys
import ssl as sslib
import select
from io import BytesIO
from io import BufferedRandom
from binascii import hexlify
from upydevice import wsclient, wsprotocol
from .exceptions import DeviceException, DeviceNotFound
try:
    from upydev import __path__ as ca_PATH
    CA_PATH = ca_PATH[0]
except Exception:
    CA_PATH = None


_REPR_CMDS_LIST = ["os.uname().sysname",
                   "os.uname().release",
                   "os.uname().version",
                   "os.uname().machine",
                   "machine.unique_id()",
                   "sys.implementation.name"]
_REPR_IMPORTS = ["import sys", "import os",
                 "import machine", "import network",
                 "nic=network.WLAN(network.STA_IF)"]

REPR_IMPORTS_CMD = ';'.join(_REPR_IMPORTS)
REPR_CMDS = f'[{",".join(_REPR_CMDS_LIST)}' + ",{}]"


def get_ssid():
    if sys.platform == "linux" or sys.platform == "linux2":
        ssid = ''
        try:
            output = subprocess.check_output(['sudo', 'iwgetid'])
            ssid = output.split('"')[1]
        except Exception as e:
            print(e)
        return ssid
    elif sys.platform == "darwin":
        # MAC OS X
        scanoutput = subprocess.check_output(["airport", "-I"])
        wifi_info = [data.strip()
                     for data in scanoutput.decode('utf-8').split('\n')]
        wifi_info_dic = {data.split(':')[0]: data.split(
            ':')[1].strip() for data in wifi_info[:-1]}
        return wifi_info_dic['SSID']


# find devices in wlan with port 8266/8833 open/listening
def net_scan(n=None, debug=False, ssl=False, debug_info=False):
    WebREPL_port = 8266
    if ssl:
        WebREPL_port = 8833
    if debug:
        print('Scanning WLAN {} for upy devices...'.format(get_ssid()))
    gws = netifaces.gateways()
    host_range = "{}-255".format(gws['default'][netifaces.AF_INET][0])
    nmScan = nmap.PortScanner()
    n_scans = 1
    netdevices = []
    if n is not None:
        n_scans = n
    for i in range(n_scans):
        if debug:
            print('SCAN # {}'.format(i))
        my_scan = nmScan.scan(
            hosts=host_range, arguments='-p {}'.format(WebREPL_port))
        hosts_list = [{'host': x, 'state': nmScan[x]['status']['state'], 'port':list(
            nmScan[x]['tcp'].keys())[0],
            'status':nmScan[x]['tcp'][WebREPL_port]['state']}
            for x in nmScan.all_hosts()]
        devs = [host for host in hosts_list if host['status'] == 'open']
        if debug:
            print('FOUND {} device/s :'.format(len(devs)))
        N = 1
        if debug:
            for dev in devs:
                try:
                    print('DEVICE {}: , IP: {} , STATE: {}, PORT: {}, '
                          'STATUS: {}'.format(N, dev['host'], dev['state'],
                                              dev['port'], dev['status']))
                    N += 1
                except Exception:
                    pass
        if not debug_info:
            for dev in devs:
                if dev['host'] not in netdevices:
                    netdevices.append(dev['host'])
            return netdevices
        else:
            return devs


class BASE_WS_DEVICE:
    def __init__(self, target, password, init=False, ssl=False, auth=False,
                 capath=CA_PATH, passphrase=None):
        self.ws = None
        self.ip = target
        if ':' in password:
            self.pswd, self.passphrase = password.split(':')
        else:
            self.pswd = password
            self.passphrase = passphrase
        if ':' in target:
            self.ip, self.port = target.split(':')
            self.port = int(self.port)
        else:
            self.port = 8266
        self.hostname = None
        self.hostname_mdns = None
        self.bytes_sent = 0
        self.buff = b''
        self.raw_buff = b''
        self.prompt = b'>>> '
        self.response = ''
        self._kbi = '\x03'
        self._banner = '\x02'
        self._reset = '\x04'
        self._hreset = "import machine; machine.reset()\r"
        self._traceback = b'Traceback (most recent call last):'
        self._flush = b''
        self.linebuffer = BufferedRandom(BytesIO())
        self._debug = False
        self.output = None
        self.platform = None
        self.connected = False
        self.repl_CONN = self.connected
        self._ssl = ssl
        self._uriprotocol = 'ws'
        if ssl:
            self._uriprotocol = 'wss'
        if init:
            ip_now = None
            if self.passphrase:
                auth = True
                ssl = True
                self._uriprotocol = 'wss'
                if self.port == 8266:
                    self.port = 8833

            if self.ip.endswith('.local'):
                self.hostname = self.ip
                self.hostname_mdns = self.ip
                try:
                    ip_now = socket.gethostbyname(self.hostname)
                except socket.gaierror:
                    raise DeviceNotFound(f"WebSocketDevice @ "
                                         f"{self._uriprotocol}:"
                                         f"//{self.ip}:{self.port} is not reachable")

            if not ssl:
                self._uriprotocol = 'ws'
                self.ws = wsclient.connect(
                    f'ws://{self.ip}:{self.port}', self.pswd)
            else:
                if self.port == 8266:
                    self.port = 8833
                self._uriprotocol = 'wss'
                self.ws = wsclient.connect(
                    f'wss://{self.ip}:{self.port}', self.pswd,
                    auth=auth, capath=capath, passphrase=self.passphrase)
            if self.ws:
                self.connected = True
                # resolve name, store ip in self.ip
                # store mdns name in self.hostname
                if ip_now:
                    self.ip = ip_now
                self.repl_CONN = self.connected
            else:
                raise DeviceNotFound(f"WebSocketDevice @ "
                                     f"{self._uriprotocol}:"
                                     f"//{self.ip}:{self.port} is not reachable")

    def open_wconn(self, ssl=False, auth=False, capath=CA_PATH):
        try:
            ip_now = None
            if self.passphrase:
                auth = True
                ssl = True
                self._uriprotocol = 'wss'
                if self.port == 8266:
                    self.port = 8833

            if self.ip.endswith('.local'):
                self.hostname = self.ip
                self.hostname_mdns = self.ip
                try:
                    ip_now = socket.gethostbyname(self.hostname)
                except socket.gaierror:
                    raise DeviceNotFound(f"WebSocketDevice @ "
                                         f"{self._uriprotocol}:"
                                         f"//{self.ip}:{self.port} is not reachable")

            if not ssl:
                self._uriprotocol = 'ws'
                if self.port == 8833:
                    self.port = 8266
                self.ws = wsclient.connect(
                    f'ws://{self.ip}:{self.port}', self.pswd)
            else:
                self._uriprotocol = 'wss'
                if self.port == 8266:
                    self.port = 8833
                if self.passphrase:
                    auth = True
                self.ws = wsclient.connect(
                    f'wss://{self.ip}:{self.port}', self.pswd,
                    auth=auth, capath=capath, passphrase=self.passphrase)
            if self.ws:
                self.connected = True
                self.repl_CONN = self.connected
                if ip_now:
                    self.ip = ip_now
            else:
                raise DeviceNotFound(f"WebSocketDevice @ "
                                     f"{self._uriprotocol}:"
                                     f"//{self.ip}:{self.port} is not reachable")
        except sslib.SSLError:
            raise sslib.SSLError
        except Exception as e:
            print(e)

    def close_wconn(self):
        if self.ws:
            self.ws.close()
        self.connected = False
        if self.hostname_mdns:
            self.ip = self.hostname_mdns
        self.repl_CONN = self.connected
        time.sleep(0.1)

    def connect(self, **kargs):
        self.open_wconn(**kargs)

    def disconnect(self):
        self.close_wconn()

    @property
    def address(self):
        return self.ip

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, opt):
        assert isinstance(opt, bool)
        self._debug = opt
        self.ws.debug = opt

    def write(self, cmd):
        n_bytes = len(bytes(cmd, 'utf-8'))
        self.ws.send(cmd)
        return n_bytes

    def read_all(self):
        self.ws.sock.settimeout(None)
        try:
            self.raw_buff = b''
            while self.prompt not in self.raw_buff:
                try:
                    fin, opcode, data = self.ws.read_frame()
                    self.raw_buff += data
                except AttributeError:
                    pass

            return self.raw_buff
        except socket.timeout:
            return self.raw_buff

    def flush(self):
        self.ws.sock.settimeout(0.01)
        self._flush = b''
        self.linebuffer.truncate(0)
        self.linebuffer.seek(0)
        self.ws.reset_buffers()
        while self.ws_readable():
            while True:
                try:
                    fin, opcode, data = self.ws.read_frame()
                    self._flush += data
                except socket.timeout:
                    break
                except wsprotocol.NoDataException:
                    break
        self.ws.reset_buffers()

    def ws_readable(self):
        for i in range(3):
            try:
                readable, writable, exceptional = select.select([self.ws.sock],
                                                                [self.ws.sock],
                                                                [self.ws.sock])
                if readable:
                    return True
                else:
                    return False
            except Exception as e:
                if self.debug:
                    print(e)
                time.sleep(0.01)

    def wr_cmd(self, cmd, silent=False, rtn=True, rtn_resp=False,
               long_string=False):
        self.output = None
        self.response = ''
        self.buff = b''
        self.flush()
        self.bytes_sent = self.write(cmd+'\r')
        # time.sleep(0.1)
        # self.buff = self.read_all()[self.bytes_sent:]
        self.buff = self.read_all()
        if self.buff == b'':
            # time.sleep(0.1)
            self.buff = self.read_all()
        # print(self.buff)
        # filter command
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

    def cmd(self, cmd, silent=False, rtn=False, long_string=False):
        disconnect_on_end = not self.connected
        if not self.connected:
            self.open_wconn(ssl=self._ssl, auth=True)
        self.wr_cmd(cmd, silent=True, long_string=long_string)
        if self.connected:
            if disconnect_on_end:
                self.close_wconn()
        self.get_output()
        if not silent:
            print(self.response)
        if rtn:
            return self.output

    def reset(self, silent=False, reconnect=True, hr=False):
        if not silent:
            print('Rebooting device...')
        if self.connected:
            if not hr:
                self.bytes_sent = self.write(self._reset)
            else:
                self.bytes_sent = self.write(self._hreset)
            if self._uriprotocol == 'ws':
                time.sleep(0.2)
            else:
                time.sleep(1)
            self.close_wconn()
            if reconnect:
                time.sleep(1)
                while True:
                    try:
                        self.open_wconn(ssl=self._ssl, auth=True)
                        self.wr_cmd(self._banner, silent=True)
                        break
                    except Exception:
                        time.sleep(0.5)
                        self.ws._close()
                self.cmd('')
            if not silent:
                print('Done!')
        else:
            self.open_wconn(ssl=self._ssl, auth=True)
            if not hr:
                self.bytes_sent = self.write(self._reset)
            else:
                self.bytes_sent = self.write(self._hreset)
            if self._uriprotocol == 'ws':
                time.sleep(0.2)
            else:
                time.sleep(1)
            self.close_wconn()
            if not silent:
                print('Done!')

    def kbi(self, silent=True, pipe=None, long_string=False):
        if self.connected:
            if pipe is not None:
                self.wr_cmd(self._kbi, silent=silent)
                bf_output = self.response.split('Traceback')[0]
                traceback = 'Traceback' + self.response.split('Traceback')[1]
                if bf_output != '' and bf_output != '\n':
                    pipe(bf_output)
                pipe(traceback, std='stderr')
            else:
                self.wr_cmd(self._kbi, silent=silent, long_string=long_string)
                self.cmd('')
        else:
            self.cmd(self._kbi, silent=silent)
            self.cmd('')

    def banner(self, pipe=None):
        self.wr_cmd(self._banner, silent=True, long_string=True)
        if pipe is None:
            print(self.response.replace('\n\n', '\n'))
        else:
            pipe(self.response.replace('\n\n', '\n'))

    def get_output(self):
        try:
            self.output = ast.literal_eval(self.response)
        except Exception:
            if 'bytearray' in self.response:
                try:
                    self.output = bytearray(ast.literal_eval(
                        self.response.strip().split('bytearray')[1]))
                except Exception:
                    pass
            else:
                if 'array' in self.response:
                    try:
                        arr = ast.literal_eval(
                            self.response.strip().split('array')[1])
                        self.output = array(arr[0], arr[1])
                    except Exception:
                        pass
            pass


class WS_DEVICE(BASE_WS_DEVICE):
    def __init__(self, target, password, init=False, ssl=False, auth=False,
                 capath=CA_PATH, name=None, dev_platf=None,
                 autodetect=False, passphrase=None):
        super().__init__(target=target, password=password, init=init, ssl=ssl,
                         auth=auth, capath=capath, passphrase=passphrase)
        self.dev_class = 'WebSocketDevice'
        self.dev_platform = dev_platf
        self.name = name
        self.raw_buff = b''
        self.message = b''
        self.output_queue = multiprocessing.Queue(maxsize=1)
        self.data_buff = ''
        self.datalog = []
        self.paste_cmd = ''
        self.flush_conn = self.flush
        self._is_traceback = False
        self.stream_kw = ['print', 'ls', 'cat', 'help', 'from', 'import',
                          'tree', 'du']
        if name is None and self.dev_platform:
            self.name = '{}_{}'.format(
                self.dev_platform, self.ip.split('.')[-1])
        if autodetect:
            if not self.connected:
                self.cmd("import gc;import sys; sys.platform", silent=True)
            else:
                self.wr_cmd("import gc;import sys; sys.platform", silent=True)
            self.dev_platform = self.output
            if not self.name:
                self.name = '{}_{}'.format(
                    self.dev_platform, self.ip.split('.')[-1])

    def __repr__(self):
        disconnect_on_end = False
        if not self.connected:
            disconnect_on_end = True
            self.connect()
        repr_cmd = ';'.join([REPR_IMPORTS_CMD, REPR_CMDS])
        if self.ip == '192.168.4.1':
            rssi = 0
            (self.dev_platform, self._release,
             self._version, self._machine, uuid, imp, _) = self.wr_cmd(repr_cmd,
                                                                       silent=True,
                                                                       rtn_resp=True)
        else:
            repr_cmd = repr_cmd.format(
                "nic.status('rssi'), nic.config('dhcp_hostname')")
            (self.dev_platform, self._release,
             self._version, self._machine, uuid, imp, rssi,
             self.hostname) = self.wr_cmd(repr_cmd, silent=True, rtn_resp=True)
        # uid = self.wr_cmd("from machine import unique_id; unique_id()",
        #                   silent=True, rtn_resp=True)
        vals = hexlify(uuid).decode()
        imp = imp[0].upper() + imp[1:]
        imp = imp.replace('p', 'P')
        self._mac = ':'.join([vals[i:i+2] for i in range(0, len(vals), 2)])
        fw_str = f'{imp} {self._version}; {self._machine}'
        if self.hostname:
            dev_str = (f'(MAC: {self._mac}, Host Name: {self.hostname}, '
                       f'RSSI: {rssi} dBm)')
        else:
            dev_str = f'(MAC: {self._mac}, RSSI: {rssi} dBm)'
        if disconnect_on_end:
            self.disconnect()
        if self.hostname:
            if not self.hostname.endswith('.local'):
                self.hostname += '.local'

        return (f'WebSocketDevice @ {self._uriprotocol}://{self.ip}:{self.port},'
                f' Type: {self.dev_platform}, Class: {self.dev_class}\n'
                f'Firmware: {fw_str}\n{dev_str}')

    def readline(self):
        self.ws.sock.settimeout(None)
        try:
            self.raw_buff = b''
            data = b''
            state = 0
            # Consume frames until eol
            while b'\r\n' not in data:
                fin, opcode, data = self.ws.read_frame()
                self.linebuffer.write(data)
                if not fin:
                    if self.debug:
                        print(f"\nFIN: {fin} | OPCODE: {opcode} | DATA: {data}\n")
                if self.prompt in data:
                    if data.endswith(self.prompt):
                        break

            self.linebuffer.seek(0)
            while not self.raw_buff.endswith(b'\r\n'):
                state = 1
                self.raw_buff += self.linebuffer.read(1)
                if self.raw_buff.endswith(self.prompt):
                    if not self.linebuffer.peek(1):
                        break
            rest = self.linebuffer.read()
            self.linebuffer.truncate(0)
            self.linebuffer.seek(0)
            self.linebuffer.write(rest)
            if self.debug and not fin:
                print(self.raw_buff)
            return self.raw_buff

        except socket.timeout as e:
            if self.debug:
                print(e)
            return self.raw_buff
        except KeyboardInterrupt:
            if self.debug:
                print(f'Interrupted in readline: state {state}; data: {data}')
                print(self.raw_buff)
            raise KeyboardInterrupt

    def wr_cmd(self, cmd, silent=False, rtn=True, long_string=False,
               rtn_resp=False, follow=False, pipe=None, multiline=False,
               dlog=False, nb_queue=None):
        self.output = None
        self._is_traceback = False
        self.response = ''
        self.buff = b''
        self.flush()
        self.bytes_sent = self.write(cmd+'\r')
        # time.sleep(0.1)
        # self.buff = self.read_all()[self.bytes_sent:]
        if not follow:
            self.buff = self.read_all()
        if self.buff == b'':
            # time.sleep(0.1)
            if not follow:
                self.buff = self.read_all()
            else:
                silent_pipe = silent
                silent = True
                rtn = False
                rtn_resp = False
                try:
                    self.follow_output(cmd, pipe=pipe, multiline=multiline,
                                       silent=silent_pipe)
                except KeyboardInterrupt:
                    # time.sleep(0.2)
                    self.paste_cmd = ''
                    if pipe is None:
                        print('')
                        self.kbi(pipe=pipe, silent=False,
                                 long_string=long_string)  # KBI
                    else:
                        self.kbi(pipe=pipe)  # KBI
                    time.sleep(0.2)
                    for i in range(1):
                        self.write('\r')
                        self.flush_conn()
        # print(self.buff)
        # filter command
        cmd_filt = bytes(cmd + '\r\n', 'utf-8')
        self.buff = self.buff.replace(cmd_filt, b'', 1)
        if dlog:
            self.data_buff = self.buff.replace(b'\r', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode('utf-8', 'ignore')
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
                if pipe is None:
                    try:
                        if self._traceback.decode() in self.response:
                            exception_msg = ' '.join(['Traceback',
                                                      self.response.split('Trac'
                                                                          'eback')[1]])
                            raise DeviceException(exception_msg)
                        else:
                            print(self.response)
                    except Exception as e:
                        print(e)
                        self.response = ''
                        self.output = ''
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
                if nb_queue.empty():
                    nb_queue.put((self.output), block=False)
                else:
                    nb_queue.get_nowait()
                    nb_queue.put((self.output), block=False)
        if rtn_resp:
            return self.output

    def follow_output(self, inp, pipe=None, multiline=False, silent=False):
        self.raw_buff = self.readline()
        if pipe is not None:
            self._is_first_line = True
            if any(_kw in inp for _kw in self.stream_kw):
                self._is_first_line = False
            if self.paste_cmd != '':
                dec_buff = self.raw_buff.decode('utf-8', 'ignore')
                while self.paste_cmd.split('\n')[-1] not in dec_buff:
                    self.raw_buff = self.readline()
                    dec_buff = self.raw_buff.decode('utf-8', 'ignore')
        while True:
            if self.raw_buff.endswith(self.prompt) and not self.ws_readable():
                break
            self.message = self.readline()
            self.buff += self.message
            # self.raw_buff += self.message
            if self.message == b'':
                if self.buff.endswith(self.prompt):
                    break
            else:
                if self.message.startswith(b'\n'):
                    self.message = self.message[1:]
                if pipe:
                    cmd_filt = bytes(inp + '\r\n', 'utf-8')
                    self.message = self.message.replace(cmd_filt, b'', 1)
                msg = self.message.replace(
                    b'\r', b'').decode('utf-8', 'ignore')
                if 'cat' in inp:
                    if msg.endswith('>>> '):
                        msg = msg.replace('>>> ', '')
                        if not msg.endswith('\n'):
                            msg = msg+'\n'

                if pipe is not None:
                    if msg == '>>> ':
                        pass
                    else:
                        pipe_out = msg.replace('>>> ', '')
                        if pipe_out != '':
                            # if '...' in pipe_out:
                            #     pipe(pipe_out.split('...')[-1])
                            # else:
                            if 'Traceback (most' in pipe_out:
                                self._is_traceback = True
                                # catch before traceback:
                                pipe_stdout = pipe_out.split(
                                    'Traceback (most')[0]
                                if pipe_stdout != '' and pipe_stdout != '\n':
                                    pipe(pipe_stdout)
                                pipe_out = 'Traceback (most' + \
                                    pipe_out.split('Traceback (most')[1]
                            if self._is_traceback:
                                pipe(pipe_out, std='stderr')
                            else:
                                if self._is_first_line:
                                    self._is_first_line = False
                                    if not multiline:
                                        pipe(pipe_out, execute_prompt=True)
                                    else:
                                        pipe(pipe_out)
                                else:
                                    pipe(pipe_out)
                if pipe is None:
                    if not silent:
                        print(msg.replace('>>> ', ''), end='')
            if self.buff.endswith(self.prompt):
                if not self.ws_readable():
                    break
        self.paste_cmd = ''

    def is_reachable(self, n_tries=2, max_loss=1, debug=False, timeout=2, zt=False):
        if zt:
            ping_cmd_str = f'ssh {zt["fwd"]} ping -c {n_tries} {zt["dev"]} -t {timeout}'
        else:
            if self.ip.endswith('.local'):
                ping_cmd_str = 'ping -c {} {} '.format(n_tries, self.ip)
            else:
                ping_cmd_str = 'ping -c {} {} -t {}'.format(n_tries, self.ip, timeout)
        ping_cmd = shlex.split(ping_cmd_str)
        timeouts = 0
        down_kw = ['Unreachable', 'down', 'timeout', 'Unknown']
        try:
            proc = subprocess.Popen(
                ping_cmd, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            while proc.poll() is None:
                resp = proc.stdout.readline()[:-1].decode()
                if debug:
                    print(resp)
                if any([kw in resp for kw in down_kw]):
                    timeouts += 1

            time.sleep(1)
            result = proc.stdout.readlines()
            for message in result:
                if debug:
                    print(message[:-1].decode())

        except KeyboardInterrupt:
            time.sleep(1)
            result = proc.stdout.readlines()
            for message in result:
                if debug:
                    print(message[:-1].decode())

        if timeouts >= max_loss:
            if debug:
                print('DEVICE IS DOWN OR SIGNAL RSSI IS TOO LOW')
            return False
        else:
            return True

    def paste_buff(self, long_command, flush=True):
        self.paste_cmd = long_command
        self.write('\x05')
        self.flush_conn()
        paste_echo = ''
        lines = long_command.split('\n')
        for line in lines:
            time.sleep(0.1)
            self.write(line+'\n')
        if flush:
            try:
                while long_command.split('\n')[-1] not in paste_echo:
                    fin, op, data = self.ws.read_frame()
                    paste_echo = data.decode('utf-8', 'ignore')
                self.flush_conn()
                while self.ws_readable():
                    time.sleep(0.1)
            except socket.timeout:
                pass

    def get_datalog(self, dvars=None, fs=None, time_out=None, units=None):
        self.datalog = []
        self.output = None
        for line in self.data_buff.splitlines():
            self.output = None
            self.response = line
            self.get_output()
            if self.output is not None and self.output != '':
                self.datalog.append(self.output)
        if dvars is not None and self.datalog != []:
            temp_dict = {var: [] for var in dvars}
            temp_dict['vars'] = dvars
            for data in self.datalog:
                if len(data) == len(dvars):
                    for i in range(len(data)):
                        temp_dict[dvars[i]].append(data[i])
            if time_out is not None:
                fs = int((1/time_out)*1000)
            if fs is not None:
                temp_dict['fs'] = fs
                temp_dict['ts'] = [i/temp_dict['fs']
                                   for i in range(len(temp_dict[dvars[0]]))]
            if units is not None:
                temp_dict['u'] = units
            self.datalog = temp_dict

    def cmd(self, cmd, silent=False, rtn=True, rtn_resp=False, nb_queue=None,
            long_string=False):
        disconnect_on_end = not self.connected
        if not self.connected:
            self.open_wconn(ssl=self._ssl, auth=True)
        self.wr_cmd(cmd, rtn=rtn, silent=True, long_string=long_string)
        if self.connected:
            if disconnect_on_end:
                self.close_wconn()
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
                    self.output = ''
            else:
                self.response = ''
        if rtn_resp:
            return self.output
        if nb_queue is not None:
            if nb_queue.empty():
                nb_queue.put((self.output), block=False)
            else:
                nb_queue.get_nowait()
                nb_queue.put((self.output), block=False)

    def cmd_nb(self, command, silent=False, rtn=True, long_string=False,
               rtn_resp=False, follow=False, pipe=None, multiline=False,
               dlog=False, block_dev=True):
        # do a
        if self.connected:
            if block_dev:
                self.dev_process_raw = multiprocessing.Process(
                    target=self.wr_cmd, args=(command, silent, rtn, long_string,
                                              rtn_resp,
                                              follow, pipe, multiline, dlog,
                                              self.output_queue))
                self.dev_process_raw.start()
            else:
                self.bytes_sent = self.write(command+'\r')
        else:
            if block_dev:
                self.dev_process_raw = multiprocessing.Process(
                    target=self.cmd, args=(command, silent, rtn, rtn_resp,
                                           self.output_queue, long_string))
                self.dev_process_raw.start()
            else:
                self.open_wconn(ssl=self._ssl, auth=True)
                self.bytes_sent = self.write(command+'\r')
                time.sleep(1)
                self.close_wconn()

    def get_opt(self):
        try:
            self.output = self.output_queue.get(block=False)
        except Exception:
            pass

    def get_RSSI(self):
        rssi_cmd = "import network;network.WLAN(network.STA_IF).status('rssi')"
        return self.cmd(rssi_cmd, silent=True, rtn_resp=True)


class WebSocketDevice(WS_DEVICE):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
