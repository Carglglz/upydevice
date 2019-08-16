# uPydevice

###Python lib to interface with micropython devices through WebREPL protocol.

#### Example usage:
### Setup and configurate a device :
    from upydevice import UPYDEVICE
    esp32 = UPYDEVICE('192.168.1.56', 'mypass') # (target_ip, password)
### Send command:

    >>> esp32.cmd('led.on()')
    >>> esp32.cmd("uos.listdir('/')")
    ['boot.py', 'webrepl_cfg.py', 'main.py']
    >>> esp32.cmd('foo()')
    >>> esp32.cmd('x = [1,2,3];my_var = len(x);print(my_var)')
    3
### Send command and store output:
    >>> resp = esp32._cmd_r("uos.listdir('/')", pt=True) # pt --> print flag; set to True to print output
    ['boot.py', 'webrepl_cfg.py', 'main.py']
    >>> resp
    ['boot.py', 'webrepl_cfg.py', 'main.py']
