# @Author: carlosgilgonzalez
# @Date:   2019-08-16T00:57:12+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-10-21T01:01:29+01:00

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
    >>> pyboard.cmd('pyb.LED(1).toggle()',timeout=100)
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

GROUP (to send commands to several devices at a time)
# Setup and configurate the devices :
    >>> from upydevice import W_UPYDEVICE, PYBOARD, GROUP
# PYBOARD
    >>> pyboard = PYBOARD('/dev/tty.usbmodem387E386731342')
# ESP32
    >>> esp32_A = W_UPYDEVICE('192.168.1.53', 'mypass')
    >>> esp32_B = W_UPYDEVICE('192.168.1.40', 'mypass')

# Setup and configurate the group:
    >>> my_group = GROUP([esp32_A, esp32_B, pyboard])

# Each upydevice has a name attribute that can be set at creation momment or after
# pyboard = PYBOARD('/dev/tty.usbmodem387E386731342', name='my_pyboard_1'); or pyboard.name = 'my_pyboard_1')
# If not set an automatic name will be set as 'upydev_class'+'ip or serial port'

# Send command:
    >>> my_group.cmd('import machine;import ubinascii;ubinascii.hexlify(machine.unique_id())')
    Sending command to wupydev_53
    b'30aea4233564'

    Sending command to wupydev_40
    b'807d3a809b30'

    Sending command to pyboard_tty.usbmodem387E386731342
    b'33004e000351343134383038'

# There is an option to silent the group messages with group_silent = True, and or each device ouput with device_silent=True

# Output is stored in group output attribute:
    >>> my_group.output
    {'wupydev_53': b'30aea4233564', 'wupydev_40': b'807d3a809b30', 'pyboard_tty.usbmodem387E386731342': b'33004e000351343134383038'}

# Send command parallel mode **: (experimental mode, may not work 100% of the times, depends on the connection quality (for wireless devices))
    >>> my_group.cmd_p('6*12')
    Sending command to: wupydev_53, wupydev_40, pyboard_tty.usbmodem387E386731342
    72


    72

    72

    Done!
# To see which ouput corresponds to which device use 'id=True' parameter:

    >>> my_group.cmd_p('ubinascii.hexlify(machine.unique_id())', id=True)
    Sending command to: wupydev_53, wupydev_40, pyboard_tty.usbmodem387E386731342
    pyboard_tty.usbmodem387E386731342:b'33004e000351343134383038'
    pyboard_tty.usbmodem387E386731342:
    pyboard_tty.usbmodem387E386731342:
    wupydev_40:b'807d3a809b30'
    wupydev_53:b'30aea4233564'
    wupydev_40:
    wupydev_53:
    Done!
    >>>
    >>> my_group.output
    {'wupydev_53': b'30aea4233564', 'wupydev_40': b'807d3a809b30', 'pyboard_tty.usbmodem387E386731342': b'33004e000351343134383038'}
"""

from .upydevice import *
name = 'upydevice'
