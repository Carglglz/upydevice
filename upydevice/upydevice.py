from .legacy import *
from .serialdevice import *
from .websocketdevice import *
from .devgroup import *
from .decorators import *
from .bledevice import *
from ipaddress import ip_address


def check_device_type(dev_address):
    if isinstance(dev_address, str):
        if '.' in dev_address and dev_address.count('.') == 3:
            # check IP
            try:
                ip_address(dev_address)
                return 'WebSocketDevice'
            except Exception as e:
                print(e)
        elif 'COM' in dev_address or '/dev/' in dev_address:
            return 'SerialDevice'
        elif len(dev_address.split('-')) == 5:
            try:
                assert [len(s) for s in dev_address.split('-')] == [8, 4, 4, 4, 12], dev_address
                return 'BleDevice'
            except Exception as e:
                print('uuid malformed')
    else:
        pass

def Device(dev_address, password=None, **kargs):
    """Returns Device class depending on dev_address type"""
    dev_type = check_device_type(dev_address)
    if dev_type == 'SerialDevice':
        return SerialDevice(dev_address, **kargs)
    if dev_type == 'WebSocketDevice':
        return WebSocketDevice(dev_address, password, **kargs)
    if dev_type == 'BleDevice':
        return BleDevice(dev_address, **kargs)
