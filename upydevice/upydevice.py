#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2019-07-11T23:33:30+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-09-14T04:11:09+01:00

import ast
import subprocess
import shlex
import time
import serial
import struct


"""
Python lib to interface with micropython devices through WebREPL protocol or
through Serial connection.

Example usage:

WIRELESS DEVICE (WebREPL)
    >>> from upydevice import W_UPYDEVICE
# Setup and configurate a device :
    >>> esp32 = W_UPYDEVICE('192.168.1.56', 'mypass') # (target_ip, password)
# Send command:
    >>> esp32.cmd('led.on()')
    >>> esp32.cmd("uos.listdir('/')")
    ['boot.py', 'webrepl_cfg.py', 'main.py'] # this output is stored in [upydevice].output
    >>> esp32.output
    ['boot.py', 'webrepl_cfg.py', 'main.py']
    >>> esp32.cmd('foo()')
    >>> esp32.cmd('x = [1,2,3];my_var = len(x);print(my_var)')
    3
# Soft Reset:
    >>> esp32.reset()
    Rebooting device...

    ### closed ###

    Done!

SERIAL DEVICE (Picocom, Pyserial)
    >>> from upydevice import S_UPYDEVICE
# Setup and configurate a device :
    >>> esp32 = S_UPYDEVICE('/dev/tty.SLAB_USBtoUART', 1000, 115200) # defaults (serial_port, timeout=1000, baudrate=9600)
# Send command:
    >>> esp32.cmd('led.on()')
    >>> esp32.cmd("uos.listdir('/')")
    ['boot.py', 'webrepl_cfg.py', 'main.py'] # this output is stored in [upydevice].output
    >>> esp32.output
    ['boot.py', 'webrepl_cfg.py', 'main.py']
    >>> esp32.cmd('foo()')
    >>> esp32.cmd('x = [1,2,3];my_var = len(x);print(my_var)')
    3
# Soft Reset:
    >>> esp32.reset()
    Rebooting device...
    Done!

PYBOARD (Picocom, Pyserial)
    >>> from upydevice import PYBOARD
# Setup and configurate a device :
    pyboard = PYBOARD('/dev/tty.usbmodem3370377430372') # defaults (serial_port, timeout=1000, baudrate=9600)
# Send command:
    >>> pyboard.cmd('pyb.LED(1).toggle()',100)
    >>> pyboard.cmd("import uos;uos.listdir('/flash')")
    ['main.py', 'pybcdc.inf', 'README.txt', 'boot.py', '.fseventsd', '.Trashes'] # this output is stored in [upydevice].output
    >>> pyboard.output
    ['main.py', 'pybcdc.inf', 'README.txt', 'boot.py', '.fseventsd', '.Trashes']
    >>> pyboard.cmd('foo()')
    >>> pyboard.cmd('x = [1,2,3];my_var = len(x);print(my_var)')
    3
# Soft Reset:
    >>> pyboard.reset()
    Rebooting pyboard...
    Done!
"""
name = 'upydevice'


class W_UPYDEVICE:
    def __init__(self, ip_target, password):
        self.password = password
        self.ip = ip_target
        self.response = None
        self.output = None
        self.long_output = []

    def _send_recv_cmd2(self, cmd):  # test method
        resp_recv = False
        command = shlex.split(cmd)
        while not resp_recv:
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE)
                resp_recv = True
            except Exception as e:
                pass

        stdout = process.communicate()
        try:
            resp = ast.literal_eval(
                stdout[0].decode('utf-8').split('\n')[6][4:-1])
        except Exception as e:
            try:
                resp = stdout[0].decode('utf-8').split('\n')[6][4:-1]
            except Exception as e:
                resp = None

            pass
        return resp, stdout

    def _cmd_r(self, cmd, pt=False):  # test method
        command = 'web_repl_cmd_r  -c "{}" -p {} -t {}'.format(
            cmd, self.password, self.ip)
        resp = self._send_recv_cmd2(command)
        if pt:
            print(resp[0])
        return resp[0]

    def _cmd(self, cmd):  # test method
        command = 'web_repl_cmd -c "{}" -p {} -t {}'.format(
            cmd, self.password, self.ip)
        resp = self.send_recv_cmd2(command)
        return resp[0]

    def _run_command_rl(self, command):  # test method
        end = False
        lines = []
        process = subprocess.Popen(
            shlex.split(command), stdout=subprocess.PIPE)
        while end is not True:
            if process.poll() is None:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip().decode()
                    lines.append(line)
                    if output.strip() == b'### closed ###':
                        end = True
            else:
                break
        rc = process.poll()
        return rc, lines

    def _cmd_rl(self, command, rt=False, evl=True):  # test method
        cmd = command
        cmd_str = 'web_repl_cmd_r -c "{}" -t {} -p {}'.format(
            cmd, self.ip, self.password)
        cmd_resp = self._run_command_rl(cmd_str)
        resp = cmd_resp[1]
        output = []
        for line in resp[6:]:
            if line == '### closed ###':
                pass
            else:
                try:
                    if line[0] == '>':
                        print(line[4:])
                        output.append(line[4:])
                    else:
                        print(line)
                        output.append(line)
                except Exception as e:
                    if len(line) == 0:
                        pass
                    else:
                        print(e)
                        pass
        if rt:
            if evl:
                return ast.literal_eval(output[0])
            else:
                return output

    def cmd(self, command, capture_output=False, silent=False, bundle_dir=''):  # best method
        cmd_str = bundle_dir+'web_repl_cmd_r -c "{}" -t {} -p {}'.format(
            command, self.ip, self.password)
        # print(group_cmd_str)
        self.long_output = []
        cmd = shlex.split(cmd_str)
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            for i in range(6):
                proc.stdout.readline()
            while proc.poll() is None:
                resp = proc.stdout.readline()[:-1].decode()
                if len(resp) > 0:
                    if resp[0] == '>':
                        if not silent:
                            print(resp[4:])
                        self.response = resp[4:]
                        self.get_output()
                        if capture_output:
                            self.long_output.append(resp[4:])
                    else:
                        if not silent:
                            print(resp)
                        self.response = resp
                        self.get_output()
                        if capture_output:
                            self.long_output.append(resp)
                else:
                    if not silent:
                        print(resp)
        except KeyboardInterrupt:
            time.sleep(1)
            result = proc.stdout.readlines()
            for message in result:
                print(message[:-1].decode())

    def reset(self, bundle_dir=''):
        reset_cmd_str = bundle_dir+'web_repl_cmd_r -c "{}" -t {} -p {}'.format('D',
                                                                    self.ip, self.password)
        reset_cmd = shlex.split(reset_cmd_str)
        print('Rebooting device...')
        try:
            proc = subprocess.Popen(
                reset_cmd, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            for i in range(6):
                proc.stdout.readline()
            while proc.poll() is None:
                resp = proc.stdout.readline()[:-1].decode()
                if len(resp) > 0:
                    if resp[0] == '>':
                        print(resp[4:])
                    else:
                        print(resp)
                else:
                    print(resp)
            print('Done!')
        except KeyboardInterrupt:
            time.sleep(1)
            result = proc.stdout.readlines()
            for message in result:
                print(message[:-1].decode())

    def get_output(self):
        try:
            self.output = ast.literal_eval(self.response)
        except Exception as e:
            pass


# S_UPYDEVICE

class S_UPYDEVICE:
    def __init__(self, serial_port, timeout=100, baudrate=9600):
        self.serial_port = serial_port
        self.returncode = None
        self.timeout = timeout
        self.baudrate = baudrate
        self.picocom_cmd = shlex.split(
            'picocom -port {} -qcx {} -b{}'.format(self.serial_port, self.timeout, self.baudrate))
        self.response = None
        self.response_object = None
        self.output = None
        self.long_output = []
        self.serial = serial.Serial(self.serial_port, self.baudrate)
        self.reset()
        # self._reset()
        self.serial.close()

    def get_output(self):
        try:
            self.output = ast.literal_eval(self.response)
        except Exception as e:
            pass

    def enter_cmd(self):
        if not self.serial.is_open:
            self.serial.open()
        self.serial.write(struct.pack('i', 0x0d))  # CR
        self.serial.close()

    def cmd(self, command, capture_output=False, timeout=None, silent=False, bundle_dir=''):
        self.long_output = []
        self.picocom_cmd = shlex.split(bundle_dir+'picocom -t {} -qx {} -b{} {}'.format(
            shlex.quote(command), self.timeout, self.baudrate, self.serial_port))
        if timeout is not None:
            self.picocom_cmd = shlex.split(bundle_dir+'picocom -t {} -qx {} -b{} {}'.format(
                shlex.quote(command), timeout, self.baudrate, self.serial_port))
        try:
            proc = subprocess.Popen(
                self.picocom_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            time.sleep(0.2)
            for i in range(2):
                self.enter_cmd()
            while proc.poll() is None:
                resp = proc.stdout.readline()[:-1].decode()
                if len(resp) > 0:
                    if resp[0] == '>':
                        if not silent:
                            print(resp[4:])
                        self.response = resp[4:]
                        self.get_output()
                        if capture_output:
                            self.long_output.append(resp[4:])
                    else:
                        if resp != '{}\r'.format(command):
                            if not silent:
                                print(resp)
                        self.response = resp
                        self.get_output()
                        if capture_output:
                            self.long_output.append(resp)
                else:
                    if not silent:
                        print(resp)

        except KeyboardInterrupt:
            time.sleep(1)
            result = proc.stdout.readlines()
            for message in result:
                print(message[:-1].decode())

    def reset(self, output=True):
        if output:
            print('Rebooting upydevice...')
        if not self.serial.is_open:
            self.serial.open()
        # time.sleep(1)
        while self.serial.inWaiting() > 0:
            self.serial.read()
        # print(self.serial.inWaiting())
        # time.sleep(1)
        self.serial.write(struct.pack('i', 0x0d))
        self.serial.write(struct.pack('i', 0x04))  # EOT
        self.serial.write(struct.pack('i', 0x0d))  # CR
        self.serial.flush()
        # print(self.serial.inWaiting())
        while self.serial.inWaiting() > 0:
            self.serial.read()
        # print(self.serial.inWaiting())
        self.serial.write(struct.pack('i', 0x0d))
        # time.sleep(1)
        self.serial.close()
        if output:
            print('Done!')


# PYBOARD


class PYBOARD:
    def __init__(self, serial_port, timeout=100, baudrate=9600):
        self.serial_port = serial_port
        self.returncode = None
        self.timeout = timeout
        self.baudrate = baudrate
        self.picocom_cmd = None
        self.response = None
        self.response_object = None
        self.output = None
        self.long_output = []
        self.serial = serial.Serial(self.serial_port, self.baudrate)
        self.reset(output=False)
        self.reset(output=False)
        # self.serial.close()
        for i in range(3):
            self.enter_cmd()

    def get_output(self):
        try:
            self.output = ast.literal_eval(self.response)
        except Exception as e:
            pass

    def enter_cmd(self):
        if not self.serial.is_open:
            self.serial.open()
        self.serial.write(struct.pack('i', 0x0d))  # CR
        # self.serial.close()

    def cmd(self, command, out_print=True, capture_output=False, silent=False, timeout=None, bundle_dir=''):
        out_print = not silent
        self.long_output = []
        self.picocom_cmd = shlex.split(bundle_dir+'picocom -t {} -qx {} -b{} {}'.format(
            shlex.quote(command), self.timeout, self.baudrate, self.serial_port))
        if timeout is not None:
            self.picocom_cmd = shlex.split(bundle_dir+'picocom -t {} -qx {} -b{} {}'.format(
                shlex.quote(command), timeout, self.baudrate, self.serial_port))
        try:
            proc = subprocess.Popen(
                self.picocom_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            time.sleep(0.05) ## KEY FINE TUNNING
            for i in range(2):
                self.enter_cmd()
            while proc.poll() is None:
                resp = proc.stdout.readline()[:-1].decode()
                if len(resp) > 0:
                    if resp[0] == '>':
                        if out_print:
                            print(resp[4:])
                        self.response = resp[4:]
                        self.get_output()
                        if capture_output:
                            self.long_output.append(resp[4:])
                    else:
                        if resp != '{}\r'.format(command):
                            if out_print:
                                print(resp)
                        self.response = resp
                        self.get_output()
                        if capture_output:
                            self.long_output.append(resp)
                else:
                    print(resp)

            while self.serial.inWaiting() > 0:
                self.serial.read()

        except KeyboardInterrupt:
            time.sleep(1)
            result = proc.stdout.readlines()
            for message in result:
                print(message[:-1].decode())

    def reset(self, output=True):
        if output:
            print('Rebooting pyboard...')
        if not self.serial.is_open:
            self.serial.open()
        # time.sleep(1)
        while self.serial.inWaiting() > 0:
            self.serial.read()
        # print(self.serial.inWaiting())
        # time.sleep(1)
        self.serial.write(struct.pack('i', 0x0d))
        self.serial.write(struct.pack('i', 0x04))  # EOT
        self.serial.write(struct.pack('i', 0x0d))  # CR
        self.serial.flush()
        # print(self.serial.inWaiting())
        while self.serial.inWaiting() > 0:
            self.serial.read()
        # print(self.serial.inWaiting())
        self.serial.write(struct.pack('i', 0x0d))
        # time.sleep(1)
        # self.serial.close()
        if output:
            print('Done!')
