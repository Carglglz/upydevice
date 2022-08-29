#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 - 2022 Carlos Gil Gonzalez
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

import time
import multiprocessing
from .decorators import getsource
import functools

# DEV GROUP


class DEVGROUP:
    def __init__(self, devs=[None], name=None):
        self.name = name
        self.devs = {dev.name: dev for dev in devs}
        self.dev_process_raw_dict = None
        self.output = None
        self.output_queue = {
            dev.name: multiprocessing.Queue(maxsize=1) for dev in devs}

    def cmd(self, command, group_silent=False, dev_silent=False, ignore=[], include=[]):
        if len(include) == 0:
            include = [dev for dev in self.devs.keys()]
        for dev in ignore:
            include.remove(dev)
        for dev in include:
            if not group_silent:
                print('Sending command to {}'.format(dev))
            self.devs[dev].wr_cmd(command, silent=dev_silent)
        self.output = {dev: self.devs[dev].output for dev in include}

    def cmd_p(self, command, group_silent=False, dev_silent=False, ignore=[],
              include=[], blocking=True, id=False, rtn=True, long_string=False,
              rtn_resp=False, follow=False, pipe=None, multiline=False,
              dlog=False):
        if not id:
            self.dev_process_raw_dict = {dev: multiprocessing.Process(target=self.devs[dev].wr_cmd, args=(
                command, dev_silent, rtn, long_string, rtn_resp, follow, pipe,
                multiline, dlog, self.output_queue[dev])) for dev in self.devs.keys() if self.devs[dev].dev_class != 'BleDevice'}
            if len(include) == 0:
                include = [dev for dev in self.devs.keys()]
            for dev in ignore:
                include.remove(dev)
            if not group_silent:
                print('Sending command to: {}'.format(', '.join(include)))
            for dev in include:
                # self.devs[dev].cmd(command, silent=dev_silent)
                if self.devs[dev].dev_class != 'BleDevice':
                    self.dev_process_raw_dict[dev].start()

            while blocking:
                dev_proc_state = [self.dev_process_raw_dict[dev].is_alive(
                ) for dev in self.dev_process_raw_dict.keys()]
                if all(state is False for state in dev_proc_state):
                    time.sleep(0.1)
                    if not group_silent:
                        print('Done!')
                    break

            try:
                self.output = {dev: self.output_queue[dev].get(
                    timeout=2) for dev in include}
            except Exception as e:
                pass
            for dev in include:
                try:
                    self.devs[dev].output = self.output[dev]
                except Exception as e:
                    pass

    def get_opt(self):
        try:
            self.output = {dev: self.output_queue[dev].get(
                timeout=2) for dev in self.devs.keys()}
        except Exception as e:
            pass
        for dev in self.devs.keys():
            try:
                self.devs[dev].output = self.output[dev]
            except Exception as e:
                pass

    def reset(self, group_silent=False, silent_dev=True, ignore=[], include=[]):
        if len(include) == 0:
            include = [dev for dev in self.devs.keys()]
        for dev in ignore:
            include.remove(dev)
        for dev in include:
            if not group_silent:
                print('Rebooting {}'.format(dev))
            self.devs[dev].reset(silent=silent_dev)


class DeviceGroup(DEVGROUP):

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    def code(self, func):
        str_func = '\n'.join(getsource(func).split('\n')[1:])
        for dev in self.devs.keys():
            self.devs[dev].paste_buff(str_func)
            self.devs[dev].cmd('\x04', silent=True)

        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            self.output = {}
            for dev in self.devs.keys():
                self.devs[dev].wr_cmd(cmd_, rtn=True)
                if self.devs[dev].output:
                    self.output[dev] = self.devs[dev].output
            if self.output:
                return self.output
        return wrapper_cmd

    def code_follow(self, func):
        str_func = '\n'.join(getsource(func).split('\n')[1:])
        for dev in self.devs.keys():
            self.devs[dev].paste_buff(str_func)
            self.devs[dev].cmd('\x04', silent=True)

        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            self.output = {}
            for dev in self.devs.keys():
                self.devs[dev].wr_cmd(cmd_, rtn=True, follow=True)
                if self.devs[dev].output:
                    self.output[dev] = self.devs[dev].output
            if self.output:
                return self.output
        return wrapper_cmd
