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


from .serialdevice import *
from .websocketdevice import *
from .devgroup import *
from .decorators import *
# from .bledevice import *
from .exceptions import *
from ipaddress import ip_address
import socket


def check_device_type(dev_address, resolve_name=False):
    if isinstance(dev_address, str):
        if '.' in dev_address and dev_address.count('.') == 3:
            # check IP
            if ':' not in dev_address:
                try:
                    ip_address(dev_address)
                    return 'WebSocketDevice'
                except Exception as e:
                    print(e)
            else:
                return check_device_type(dev_address.split(':')[0], resolve_name)
        elif dev_address.endswith('.local'):
            try:
                if resolve_name:
                    return check_device_type(socket.gethostbyname(dev_address))
                else:
                    return 'WebSocketDevice'
            except Exception as e:
                print(e)
        elif '.local' in dev_address and ':' in dev_address:
            return check_device_type(dev_address.split(':')[0], resolve_name)
        elif 'COM' in dev_address or '/dev/' in dev_address:
            return 'SerialDevice'
        elif len(dev_address.split('-')) == 5:
            try:
                assert [len(s) for s in dev_address.split(
                    '-')] == [8, 4, 4, 4, 12], dev_address
                return 'BleDevice'
            except Exception as e:
                print('uuid malformed')
        elif ':' in dev_address:
            return 'BleDevice'
    else:
        if hasattr(dev_address, 'address') and hasattr(dev_address, 'details'):
            return 'BleDevice'


def Device(dev_address, password=None, **kargs):
    """Returns Device class depending on dev_address type"""
    dev_type = check_device_type(dev_address)
    if dev_type == 'SerialDevice':
        baudrt = 115200
        pop_args = ['ssl', 'auth', 'capath']
        fkargs = {k: v for k, v in kargs.items() if k not in pop_args}
        if password:
            baudrt = password
        if 'baudrate' in fkargs:
            baudrt = fkargs.pop('baudrate')
        return SerialDevice(dev_address, baudrate=baudrt, **fkargs)
    if dev_type == 'WebSocketDevice':
        return WebSocketDevice(dev_address, password, **kargs)
    if dev_type == 'BleDevice':
        from .bledevice import BleDevice
        pop_args = ['ssl', 'auth', 'capath']
        fkargs = {k: v for k, v in kargs.items() if k not in pop_args}
        return BleDevice(dev_address, **fkargs)
