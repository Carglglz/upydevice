#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2019-07-11T23:33:30+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-08-16T01:16:26+01:00

import ast
import subprocess
import shlex
import time


"""
Python lib to interface with micropython devices through WebREPL protocol.

Example usage:
# Setup and configurate a device :
    esp32 = UPYDEVICE('192.168.1.56', 'mypass') # (target_ip, password)
# Send command:
    >>> esp32.cmd('led.on()')
    >>> esp32.cmd("uos.listdir('/')")
    ['boot.py', 'webrepl_cfg.py', 'main.py']
    >>> esp32.cmd('foo()')
    >>> esp32.cmd('x = [1,2,3];my_var = len(x);print(my_var)')
    3
# Send command and store output:
    >>> resp = esp32._cmd_r("uos.listdir('/')", pt=True) # pt --> print flag; set to True to print output
    ['boot.py', 'webrepl_cfg.py', 'main.py']
    >>> resp
    ['boot.py', 'webrepl_cfg.py', 'main.py']
"""
name = 'upydevice'


class UPYDEVICE:
    def __init__(self, ip_target, password):
        self.password = password
        self.ip = ip_target

    def _send_recv_cmd2(self, cmd):
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

    def _cmd_r(self, cmd, pt=False):
        command = 'web_repl_cmd_r  -c "{}" -p {} -t {}'.format(
            cmd, self.password, self.ip)
        resp = self._send_recv_cmd2(command)
        if pt:
            print(resp[0])
        return resp[0]

    def _cmd(self, cmd):
        command = 'web_repl_cmd -c "{}" -p {} -t {}'.format(
            cmd, self.password, self.ip)
        resp = self.send_recv_cmd2(command)
        return resp[0]

    def _run_command_rl(self, command):
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

    def _cmd_rl(self, command, rt=False, evl=True):
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

    def cmd(self, command):
        cmd_str = 'web_repl_cmd_r -c "{}" -t {} -p {}'.format(
            command, self.ip, self.password)
        # print(group_cmd_str)
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
                        print(resp[4:])
                    else:
                        print(resp)
                else:
                    print(resp)
        except KeyboardInterrupt:
            time.sleep(1)
            result = proc.stdout.readlines()
            for message in result:
                print(message[:-1].decode())

    def reset(self):
        reset_cmd_str = 'web_repl_cmd_r -c "{}" -t {} -p {}'.format('D',
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
