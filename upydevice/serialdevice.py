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
import serial
import serial.tools.list_ports  # BUG: This makes pyinstaller to fail
import multiprocessing
from array import array
import glob
from binascii import hexlify
import sys
from .exceptions import DeviceException, DeviceNotFound


# https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def get_serial_port_data(serialport, debug=False):
    serial_ports = serial.tools.list_ports.comports()
    if not debug:
        for port in serial_ports:
            if port.device == serialport:
                return (port.description, port.manufacturer)

        print('Port Not Found in : {}'.format([port.device for port in serial_ports]))
    else:
        for port in serial_ports:
            if port.device == serialport:
                return (port)

        print('Port Not Found in : {}'.format([port.device for port in serial_ports]))


def list_comp_devices(debug_info=False):
    serial_ports = serial.tools.list_ports.comports()
    if not debug_info:
        return [port.device for port in serial_ports if port.vid]
    else:
        return {port.device: [port.description, port.manufacturer]
                for port in serial_ports if port.vid}


def serial_scan(debug_info=False):
    return list_comp_devices(debug_info=debug_info)


class BASE_SERIAL_DEVICE:
    def __init__(self, serial_port, baudrate):
        self.bytes_sent = 0
        self.buff = b''
        self._kbi = '\x03'
        self._banner = '\x02'
        self._reset = '\x04'
        self._hreset = 'import machine; machine.reset()\r'
        self.response = ''
        self._traceback = b'Traceback (most recent call last):'
        self.output = None
        self.wr_cmd = self.cmd
        self.prompt = b'>>> '
        self.dev_description, self.manufacturer, self._hwid = self._get_serial_port_data(
            serial_port)
        self.serial = serial.Serial(serial_port, baudrate)

    def _get_serial_port_data(self, serialport):
        serial_port_found = False
        for port in serial.tools.list_ports.comports():
            if port.device == serialport:
                serial_port_found = True
                desc = port.description.split('-')[0].strip()
                return (desc, port.manufacturer, port.hwid)

        if not serial_port_found:
            serialport = serialport.replace('tty', 'cu')
        for port in serial.tools.list_ports.comports():
            if port.device == serialport:
                serial_port_found = True
                desc = port.description.split('-')[0].strip()
                return (desc, port.manufacturer, port.hwid)

        raise DeviceNotFound('SerialDevice @ {} is not available'.format(serialport))

    def cmd(self, cmd, silent=False, rtn=True, long_string=False, rtn_resp=False):
        self.response = ''
        self.output = None
        self.buff = b''
        self.bytes_sent = self.serial.write(bytes(cmd+'\r', 'utf-8'))
        time.sleep(0.2)
        # self.buff = self.serial.read_all()[self.bytes_sent+1:]
        if self.buff == b'':
            time.sleep(0.2)
            self.buff = self.serial.read_all()
        cmd_filt = bytes(cmd + '\r\n', 'utf-8')
        self.buff = self.buff.replace(cmd_filt, b'', 1)
        if self._traceback in self.buff:
            long_string = True
        if long_string:
            self.response = self.buff.replace(b'\r', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode()
        else:
            self.response = self.buff.replace(b'\r\n', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode()
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

    def reset(self, silent=False, reconnect=True, hr=False):
        self.buff = b''
        if not silent:
            print('Rebooting device...')
        if not hr:
            self.bytes_sent = self.serial.write(bytes(self._reset, 'utf-8'))
        else:
            try:
                self.bytes_sent = self.serial.write(bytes(self._hreset, 'utf-8'))
            except OSError:
                pass
        time.sleep(0.5)
        try:
            self.buff = self.serial.read_all()
        except OSError:
            pass
        if not silent:
            print('Done!')

    def kbi(self, silent=True, pipe=None, long_string=False):
        if pipe is not None:
            self.wr_cmd(self._kbi, silent=silent)
            pipe(self.response, std='stderr')
        else:
            self.cmd(self._kbi, silent=silent, long_string=long_string)

    def banner(self, pipe=None):
        self.cmd(self._banner, silent=True, long_string=True)
        if pipe is None:
            print(self.response.replace('\n\n', '\n'))
        else:
            pipe(self.response.replace('\n\n', '\n'))

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


class SERIAL_DEVICE(BASE_SERIAL_DEVICE):
    def __init__(self, serial_port, baudrate=115200, name=None, dev_platf=None,
                 autodetect=False, init=True):
        super().__init__(serial_port=serial_port, baudrate=baudrate)
        self.dev_class = 'SerialDevice'
        self.dev_platform = dev_platf
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.name = name
        self.raw_buff = b''
        self.message = b''
        self.data_buff = ''
        self.datalog = []
        self.output_queue = multiprocessing.Queue(maxsize=1)
        self.paste_cmd = ''
        self.connected = True
        self.repl_CONN = self.connected
        self._is_traceback = False
        self._is_first_line = True
        self._machine = None
        self.stream_kw = ['print', 'ls', 'cat', 'help', 'from', 'import',
                          'tree', 'du']
        if name is None and self.dev_platform:
            self.name = '{}_{}'.format(
                self.dev_platform, self.serial_port.split('/')[-1])
        if autodetect:
            self.cmd('\r', silent=True)
            self.cmd("import gc;import sys; sys.platform", silent=True)
            self.dev_platform = self.output
            if not self.name:
                self.name = '{}_{}'.format(
                    self.dev_platform, self.serial_port.split('/')[-1])
        if init:
            self.cmd(self._kbi+'\r', silent=True)

    def __repr__(self):
        repr_cmd = "import sys;import os; from machine import unique_id; \
        [os.uname().sysname, os.uname().release, os.uname().version, \
        os.uname().machine, unique_id(), sys.implementation.name]"
        (self.dev_platform, self._release,
         self._version, self._machine, uuid, imp) = self.cmd(repr_cmd,
                                                             silent=True,
                                                             rtn_resp=True)
        vals = hexlify(uuid).decode()
        imp = imp[0].upper() + imp[1:]
        imp = imp.replace('p', 'P')
        self._mac = ':'.join([vals[i:i+2] for i in range(0, len(vals), 2)])
        fw_str = '{} {}; {}'.format(imp, self._version, self._machine)
        dev_str = '(MAC: {})'.format(self._mac)
        desc_str = '{}, Manufacturer: {}'.format(self.dev_description,
                                                 self.manufacturer)
        return (f'SerialDevice @ {self.serial_port}, Type: {self.dev_platform}, '
                f'Class: {self.dev_class}\n'
                f'Firmware: {fw_str}\n{desc_str}\n{dev_str}')

    @property
    def address(self):
        return self.serial_port

    def flush_conn(self):
        flushed = 0
        while flushed < 2:
            try:
                if self.serial.readable():
                    self.buff = self.serial.read_all()
                    flushed += 1
                    self.buff = b''
            except Exception as e:
                flushed += 1

    def _kbi_cmd(self):
        self.bytes_sent = self.serial.write(bytes(self._kbi+'\r', 'utf-8'))

    def read_until(self, exp=None, exp_p=True, rtn=False):
        self.raw_buff = b''
        while exp not in self.raw_buff:
            self.raw_buff += self.serial.read(1)
            if exp_p:
                if self.prompt in self.raw_buff:
                    break
        if rtn:
            return self.raw_buff
            # print(self.raw_buff)

    def cmd(self, cmd, silent=False, rtn=True, long_string=False,
            rtn_resp=False, follow=False, pipe=None, multiline=False,
            dlog=False, nb_queue=None):
        self._is_traceback = False
        self.response = ''
        self.output = None
        self.flush_conn()
        self.buff = b''
        self.bytes_sent = self.serial.write(bytes(cmd+'\r', 'utf-8'))
        # time.sleep(0.2)
        # self.buff = self.serial.read_all()[self.bytes_sent+1:]
        if self.buff == b'':
            if not follow:
                time.sleep(0.2)
                # self.read_until(b'\n')
                self.buff = self.serial.read_all()
                if self.buff == b'' or self.prompt not in self.buff:
                    time.sleep(0.2)
                    self.buff += self.serial.read_all()
                    while self.prompt not in self.buff:
                        self.buff += self.serial.read_all()
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
                        print('')  # print Traceback under ^C
                        self.kbi(pipe=pipe, silent=False,
                                 long_string=long_string)  # KBI
                    else:
                        self.kbi(pipe=pipe)  # KBI
                    time.sleep(0.2)
                    for i in range(1):
                        self.serial.write(b'\r')
                        self.flush_conn()
        cmd_filt = bytes(cmd + '\r\n', 'utf-8')
        self.buff = self.buff.replace(cmd_filt, b'', 1)
        if dlog:
            self.data_buff = self.buff.replace(b'\r', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode()
        if self._traceback in self.buff:
            long_string = True
        if long_string:
            self.response = self.buff.replace(b'\r', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode()
        else:
            self.response = self.buff.replace(b'\r\n', b'').replace(
                b'\r\n>>> ', b'').replace(b'>>> ', b'').decode()
        if not silent:
            if self.response != '\n' and self.response != '':
                if pipe is None:
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
                if nb_queue.empty():
                    nb_queue.put((self.output), block=False)
                else:
                    nb_queue.get_nowait()
                    nb_queue.put((self.output), block=False)
        if rtn_resp:
            return self.output

    def follow_output(self, inp, pipe=None, multiline=False, silent=False):
        self.raw_buff = b''
        # self.raw_buff += self.serial.read(len(inp)+2)
        # if not pipe:
        self.read_until(exp=b'\n')
        # self.read_until(exp=bytes(inp, 'utf-8')+b'\r\n')
        # self.read_until(exp=bytes(inp, 'utf-8'))
        if pipe is not None:
            self._is_first_line = True
            if any(_kw in inp for _kw in self.stream_kw):
                self._is_first_line = False
            if self.paste_cmd != '':
                if self.dev_platform != 'pyboard' and self.dev_platform != 'rp2':
                    while self.paste_cmd.split('\n')[-1] not in self.raw_buff.decode():
                        self.read_until(exp=b'\n')

                    self.read_until(exp=b'\n')
        while True:
            if pipe is not None and not multiline:
                self.message = b''
                while b'\n' not in self.message:
                    self.message += self.serial.read(1)
                    if self.prompt in self.message:
                        break
            else:
                self.message = b''
                while b'\r\n' not in self.message:
                    self.message += self.serial.read(1)
                    if self.prompt in self.message:
                        break
            self.buff += self.message
            self.raw_buff += self.message
            if self.message == b'':
                pass
            else:
                if self.message.startswith(b'\n') and 'ls(' not in inp:
                    self.message = self.message[1:]
                if pipe:
                    cmd_filt = bytes(inp + '\r\n', 'utf-8')
                    self.message = self.message.replace(cmd_filt, b'', 1)
                msg = self.message.replace(b'\r', b'').decode('utf-8')
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
                            if self.paste_cmd != '':
                                if self.buff.endswith(b'>>> '):
                                    # if pipe_out[-1] == '\n':
                                    pipe_out = pipe_out[:-1]
                                    if pipe_out != '' and pipe_out != '\n':
                                        if self._traceback.decode() in pipe_out:
                                            self._is_traceback = True
                                            # catch before traceback:
                                            pipe_stdout = pipe_out.split(
                                                self._traceback.decode())[0]
                                            if pipe_stdout != '' and pipe_stdout != '\n':
                                                pipe(pipe_stdout)
                                            pipe_out = self._traceback.decode(
                                            ) + pipe_out.split(self._traceback.decode())[1]
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
                                else:
                                    if self._traceback.decode() in pipe_out:
                                        self._is_traceback = True
                                        # catch before traceback:
                                        pipe_stdout = pipe_out.split(
                                            self._traceback.decode())[0]
                                        if pipe_stdout != '' and pipe_stdout != '\n':
                                            pipe(pipe_stdout)
                                        pipe_out = self._traceback.decode(
                                        ) + pipe_out.split(self._traceback.decode())[1]
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
                            else:
                                if self._traceback.decode() in pipe_out:
                                    self._is_traceback = True
                                    # catch before traceback:
                                    pipe_stdout = pipe_out.split(
                                        self._traceback.decode())[0]
                                    if pipe_stdout != '' and pipe_stdout != '\n':
                                        pipe(pipe_stdout)
                                    pipe_out = self._traceback.decode(
                                    ) + pipe_out.split(self._traceback.decode())[1]
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
                else:
                    if pipe is None:
                        if not silent:
                            print(msg.replace('>>> ', ''), end='')
            if self.buff.endswith(b'>>> '):
                break
        self.paste_cmd = ''

    def is_reachable(self):
        # portlist = [port for port in
        #             serial_ports()] + glob.glob('/dev/*')
        portlist = [p.device for p in
                    serial.tools.list_ports.comports()] + glob.glob('/dev/*')
        if self.serial.writable() and self.serial_port in portlist:
            return True
        else:
            return False

    def close_wconn(self):
        self.serial.close()
        self.connected = False

    def open_wconn(self):
        if self.serial.is_open:
            pass
        else:
            self.serial.open()
        self.connected = True

    def connect(self):
        self.open_wconn()

    def disconnect(self):
        self.close_wconn()

    def paste_buff(self, long_command):
        self.paste_cmd = long_command
        self.serial.write(b'\x05')
        lines = long_command.split('\n')
        for line in lines:
            time.sleep(0.01)
            self.serial.write(bytes(line+'\n', 'utf-8'))
        self.flush_conn()

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

    def cmd_nb(self, command, silent=False, rtn=True, long_string=False,
               rtn_resp=False, follow=False, pipe=None, multiline=False,
               dlog=False, block_dev=True):
        if block_dev:
            self.dev_process_raw = multiprocessing.Process(
                target=self.wr_cmd, args=(command, silent, rtn, long_string, rtn_resp,
                                          follow, pipe, multiline, dlog,
                                          self.output_queue))
            self.dev_process_raw.start()
        else:
            self.bytes_sent = self.serial.write(bytes(command+'\r', 'utf-8'))

    def get_opt(self):
        try:
            self.output = self.output_queue.get(block=False)
        except Exception:
            pass


class SerialDevice(SERIAL_DEVICE):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
