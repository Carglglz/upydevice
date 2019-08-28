# uPydevice

Python library to interface with Micropython devices through WebREPL protocol or through Serial connection.

### Requirements
* [upydev](https://github.com/Carglglz/upydev)
* [picocom](https://github.com/npat-efault/picocom)
* [pyserial](https://github.com/pyserial/pyserial/)

*upydev and pyserial will be automatically installed with pip*  

*to install picocom do:*  `brew install picocom`

### Install
`pip install upydevice`

#### Example usage:

### WIRELESS DEVICE (WebREPL Protocol)
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

### SERIAL DEVICE (Picocom, Pyserial)
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

### PYBOARD (Picocom, Pyserial)

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
