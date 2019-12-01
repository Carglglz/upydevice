# uPydevice DOCS

## Content

* [DEVICES](#DEVICES)
* [COMMANDS](#COMMANDS)
* [GROUP](#GROUP)
* [PARSER AND DECORATORS](#PARSER-AND-DECORATORS)
* [APP BUNDLE](#APP-BUNDLE)

------

### DEVICES:

There are three python classes that define three different MicroPython devices:

- #### W_UPYDEVICE:

  ​	The W_UPYDEVICE class, represents a wireless capable MicroPython device

  * <u>Requeriments</u>:
    1. ***Protocol : WebREPL (so this NEEDS WebREPL running on the device, see: [WebREPL](http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi) )***
    2. ***The device and the host (computer) must be connected to the same WLAN (either a local Acces Point or the one created by the device acting as an Acces Point (AP) see: [Networking](http://docs.micropython.org/en/latest/esp32/quickref.html#networking)***

  * <u>Initialization:</u>

    Once the device is running and the requeriments are met, do:

    ```python
    from upydevice import W_UPYDEVICE
    
    # BASIC INITIATION
    esp32 = W_UPYDEVICE('192.168.1.62', 'mypass') # (device ip , webrepl password)
    
    # NOW THE DEVICE IS READY
    ```

  * <u>Parameters</u>: (ip_target, password, name=None, bundle_dir=' '):
    * ip_targe: the IP of the device
    * password: the WebREPL password of the device
    * name: (optional) to give a name to the device (useful when use within a GROUP), if not set it can be set after with `esp32.name = 'esp32' `. * If not set at initialization moment, an automatic name will be set as `'upydev_class'+'ip or serial port'`, in this case would be `wupydev_62`
    * bundle_dir: to indicate the path where the binary 'web_repl_cmd_r' can be found. (This is useful when making an app bundle and this is explained further in [APP BUNDLE](#APP-BUNDLE))

  

- #### S_UPYDEVICE:

  The S_UPYDEVICE class, represents a serial capable MicroPython device

  * <u>Requeriments</u>:
    1. ***Protocol : Serial (needs Picocom and Pyserial)***
    2. ***The device and the host (computer) must be connected by USB***

  * <u>Initialization:</u>

    Once the device is running and the requeriments are met, do:

    ```python
    from upydevice import S_UPYDEVICE
    
    # BASIC INITIATION
    esp32_s = S_UPYDEVICE('/dev/tty.SLAB_USBtoUART', timeout=1000, baudrate=115200)
    
    # By default the initialization resets the device
    # NOW THE DEVICE IS READY
    ```

  * <u>Parameters</u>: (serial_port, timeout=100, baudrate=9600, name=None, bundle_dir=' '):
    * serial_port: the serial port of the device
    * timeout: the amount of time in ms that Picocom waits to receive a command output
    * baudrate: the baudrate of the serial communication
    * name: (optional) to give a name to the device (useful when use within a GROUP), if not set it can be set after with `esp32_s.name = 'esp32_s' `. * If not set at initialization moment, an automatic name will be set as `'upydev_class'+'ip or serial port'`, in this case would be `supydev_tty.SLAB_USBtoUART`
    * bundle_dir: to indicate the path where the binary 'picocom' can be found. (This is useful when making an app bundle and this is explained further in [APP BUNDLE](#APP-BUNDLE))

  

- #### PYBOARD:

  The PYBOARD class is a special class of S_UPYDEVICE and represents a Pyboard device.

  - <u>Requeriments</u>:
    1. ***Protocol : Serial (needs Picocom and Pyserial)***
    2. ***The Pyboard and the host (computer) must be connected by USB***

  * <u>Initialization:</u>

    Once the device is running and the requeriments are met, do:

    ```python
    from upydevice import PYBOARD
    
    # BASIC INITIATION
    pyboard = PYBOARD('/dev/tty.usbmodem3370377430372')
    
    # By default the initialization resets the device
    # NOW THE DEVICE IS READY
    ```

  * <u>Parameters</u>: (serial_port, timeout=100, baudrate=9600, name=None, bundle_dir=' '):
    * serial_port: the serial port of the device
    * timeout: the amount of time in ms that Picocom waits to receive a command output
    * baudrate: the baudrate of the serial communication
    * name: (optional) to give a name to the device (useful when use within a GROUP), if not set it can be set after with `pyboard.name = 'pyboard' `. * If not set at initialization moment, an automatic name will be set as `'upydev_class'+'ip or serial port'`, in this case would be `pyboard_tty.usbmodem3370377430372`
    * bundle_dir: to indicate the path where the binary 'picocom' can be found. (This is useful when making an app bundle and this is explained further in [APP BUNDLE](#APP-BUNDLE))



------

### COMMANDS:

These are the set of basic methods that each device can use:

- #### CMD

  - To send a command to the device (this is a blocking function, it won't return till the command is executed in the device)

    Example:

    ```python
    # W_UPYDEVICE
    >>> esp32.cmd('led.on()') # *led is predefined in main.py in the device
    >>> esp32.cmd("uos.listdir('/')")
    ['boot.py', 'webrepl_cfg.py', 'main.py'] # this output is stored in [upydevice].output
    >>> esp32.output
    ['boot.py', 'webrepl_cfg.py', 'main.py']
    >>> esp32.cmd('foo()')
    >>> esp32.cmd('x = [1,2,3];my_var = len(x);print(my_var)')
    3
    
    # PYBOARD
    >>> pyboard.cmd('pyb.LED(1).toggle()', timeout=100)
    >>> pyboard.cmd("import uos;uos.listdir('/flash')")
    ['main.py', 'pybcdc.inf', 'README.txt', 'boot.py', '.fseventsd', '.Trashes'] # this output is stored in [upydevice].output
    >>> pyboard.output
    ['main.py', 'pybcdc.inf', 'README.txt', 'boot.py', '.fseventsd', '.Trashes']
    >>> pyboard.cmd('foo()')
    >>> pyboard.cmd('x = [1,2,3];my_var = len(x);print(my_var)')
    3
    
    ```

    

  - <u>Options</u>: (command, silent=False, capture_output=False, timeout=None*)

    - **command**: the command to send (if using strings within the command use doble quotes for the command)

    - **silent**: this avoids printing the output of the command

    - **capture_output**: just use this if the output of the command cannot be interpreted as a python object (this will capture the raw string)

      **Special option for S_UPYDEVICE / PYBOARD*

    - **timeout**:  the amount of time in ms that Picocom waits to receive a command output

      By default uses the timeout indicated at initialization, unless is indicated with this option

- #### CMD_NB

  - To send a command to the device (this is a **non- blocking** function, it will return once the command is sent)

    Example:

    ```python
    # W_UPYDEVICE
    # Using cmd (blocking)
    >>> def test_cmd():
    ...     esp32.cmd("print('This is a message from esp32')")
    ...     print('This is a message from python3')
    ...
    >>>
    >>> test_cmd()
    This is a message from esp32
    
    This is a message from python3
    # Using cmd_nb (non-blocking)
    >>> def test_cmd_nb():
    ...     esp32.cmd_nb("print('This is a message from esp32')")
    ...     print('This is a message from python3')
    ...
    >>>
    >>> test_cmd_nb()
    This is a message from python3
    >>> This is a message from esp32
    
    ## FOR W_UPYDEVICES
    ## if the command to send is a for/while loop, to be able to stop it use the option block_dev = False, then the command esp32.kbi() (This is a KeyboardInterrupt) will stop the loop. This is because the WebREPL protocol supports one connection at a time only, so if block_dev is set to False to free this WebREPL connection.
    
    # PYBOARD
    # Using cmd (blocking)
    >>> def test_pyb_cmd():
    ...     pyboard.cmd("print('This is a message from pyboard')")
    ...     print('This is a message from python3')
    ...
    >>>
    >>> test_pyb_cmd()
    This is a message from pyboard
    
    
    This is a message from python3
    
    # Using cmd_nb (non-blocking)
    
    >>> def test_pyb_cmd_nb():
    ...     pyboard.cmd_nb("print('This is a message from pyboard')")
    ...     print('This is a message from python3')
    ...
    >>>
    >>> test_pyb_cmd_nb()
    This is a message from python3
    >>> This is a message from pyboard
    
    ```

    <u>Options</u>: (command, silent=False, *time_out=2, *block_dev=True)

    - **command**: the command to send (if using strings within the command use doble quotes for the command)

    - **silent**: this avoids printing the output of the command

      **Special options for W_UPYDEVICE*: when bloc_dev=False

      * **time_out**: the amount of time in seconds that the WebREPL connection is open (used with block_dev=False)

      * **block_dev**: to release the WebREPL connection after *time_out* seconds, this allows the following:

        *if the command to send is a for/while loop, to be able to stop it use the option block_dev = False, then the command esp32.kbi() (This is a KeyboardInterrupt) will stop the loop. This is because the WebREPL protocol supports one connection at a time only, so block_dev is set to False to free this WebREPL connection.*

    <u>Non-blocking Output</u>:

     To get output (not just print) of a non-blocking command do, ONCE THE COMMAND ENDS:

    `[upydevice].get_opt()`

    then output is stored in `[upydevice].output` 

    ```python
    # Example
    # W_UPYDEVICE
    >>> def test_cmd_nb():
    ...     esp32.cmd_nb("print('This is a message from esp32');[1,2,3]")
    ...     print('This is a message from python3')
    ...
    >>>
    >>> test_cmd_nb()
    This is a message from python3
    >>> This is a message from esp32
    [1, 2, 3]
    
    
    >>> esp32.get_opt()
    >>> esp32.output
    [1, 2, 3]
    
    # PYBOARD
    
    >>> def test_pyb_cmd_nb():
    
    ...     pyboard.cmd_nb("print('This is a message from pyboard');[1,2,3]")
    ...     print('This is a message from python3')
    ...
    >>> test_pyb_cmd_nb()
    This is a message from python3
    >>> This is a message from pyboard
    [1, 2, 3]
    
    
    
    >>> pyboard.get_opt()
    >>> pyboard.output
    [1, 2, 3]
    ```

    

- #### RESET

  * To reset the device:

    Example:

    ```python
    # W_UPYDEVICE
    >>> esp32.reset()
    Rebooting device...
    
    ### closed ###
    
    Done!
    # By default is 'verbose', to make it silent use output=False option
    >>> esp32.reset(output=False)
    >>>
    # PYBOARD
    >>> pyboard.reset()
    Rebooting pyboard...
    Done!
    # By default is 'verbose', to make it silent use output=False option
    >>> pyboard.reset(output=False)
    >>>
    ```

    

- #### KBI

  - To send  KeyboardInterrupt to the device ( this will be like doing CTRL-C in REPL)

    Use this when a for/while loop is being executed in the device to make it stop

     By default is 'verbose', to make it silent use output=False option.
    
    Ex:
    
    ```
    esp32.kbi(output=False)
    ```
    
    
  
- #### is_reachable (* Just for W_UPYDEVICE class)

  Options: (n_tries=2, max_loss=1, debug=False, timeout=2)

  - To see if a device is reachable. This command pings the device 'n_tries' times, with a threshold of 'max_loss' packet loss and a time out of 'timeout' seconds.

  - If it is reachable returns True, otherwise returns False.

    ```
    esp32.is_reachable()
    True
    ```

    

------

### GROUP:

​	This class is intended to manage/control/send commands to several devices at a time.

- <u>Initialization:</u>

​		Once a couple of devices are defined, to make a group do:

```python
# Setup and configurate the devices :
    >>> from upydevice import W_UPYDEVICE, PYBOARD, GROUP
# PYBOARD
    >>> pyboard = PYBOARD('/dev/tty.usbmodem387E386731342')
# ESP32
    >>> esp32_A = W_UPYDEVICE('192.168.1.83', 'mypass')
    >>> esp32_B = W_UPYDEVICE('192.168.1.60', 'mypass')

# Setup and configurate the group:
    >>> my_group = GROUP([esp32_A, esp32_B, pyboard])

# Each upydevice has a name attribute that can be set at creation momment or after
# pyboard = PYBOARD('/dev/tty.usbmodem387E386731342', name='my_pyboard_1'); or pyboard.name = 'my_pyboard_1')
# If not set an automatic name will be set as 'upydev_class'+'ip or serial port'
```

* <u>Parameters</u>: (devs=[])
  * **devs:** A list of devices that will be part of the group. This devices are stored in a dict in the devs attribute, so it can be accessed by  ex: `my_group.devs[esp32_A.name]` or if the device has manual set name ex: `my_group.devs['my_pyboard_1']`

- #### CMD

  To send a command to the devices in a group one device at a time (this is a blocking command, so it won't return till the last device ouput is received (*ideally))

  Example:

  ```python
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
  ```

  * <u>Parameters</u>: (command, group_silent=False, dev_silent=False, ignore=[], include=[])
    * **command**: the command to be sent to the group of devices
    * **group_silent**: by default is 'verbose' when a command is sent to each device, set True to make it silent
    * **dev_silent**: by default prints each device output, set to True to make it silent
    * **ignore:** a list of devices names to ignore, by default is empty
    * **include**: a list devices names to include, by default includes all.

- #### CMD_P

  To send a command to the devices in a group at the same time ( by default this is a blocking command, so it won't return till the last device ouput is received (*ideally) )

  ```python
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
  ```

  

  * <u>Parameters</u>: (command, group_silent=False, dev_silent=False, ignore=[], include=[], blocking=True, id=False)

    * **command**: the command to be sent to the group of devices
    * **group_silent**: by default is 'verbose' when a command is sent to the group of devices, set True to make it silent
    * **dev_silent**: by default prints each device output, set to True to make it silent
    * **ignore:** a list of devices names to ignore, by default is empty
    * **include**: a list devices names to include, by default includes all.
    * **blocking**: by default is set to True, so it will block python execution till the last device returns its output, **set it to False**, to make it **non-blocking**
    * **id**: To see which ouput corresponds to which device, set to False by default.

    Example:

    ```python
    # If using blocking=False 
    my_group = GROUP([esp32, pyboard])
    my_group.cmd_p('led.on();time.sleep(1);[1,5,7]', blocking=False)
    Sending command to: wupydev_53, pyboard_tty.usbmodem3370377430372
    [1, 5, 7]
    
    >>> [1, 5, 7]
    
    
    
    >>> my_group.output # probably will return None or the output from a previous command
    # to get the output of the non-blocking command do:
    >>> my_group.get_opt()
    >>> my_group.output
    {'wupydev_53': [1, 5, 7], 'pyboard_tty.usbmodem3370377430372': [1, 5, 7]}
    ```

    

- #### RESET

  To reset the devices of the group:

  Example:

  ```python
  >>> my_group.reset()
  Rebooting wupydev_53
  Rebooting device...
  
  ### closed ###
  
  Done!
  Rebooting pyboard_tty.usbmodem3370377430372
  Rebooting pyboard...
  Done!
  
  # By default is 'verbose', to make it silent use group_silent=True, output_dev=False option
  ```

  * <u>Parameters</u>: (group_silent=False, output_dev=True, ignore=[], include=[])

    * **group_silent**: to make the group 'verbose' ouput silent
    * **output_dev**: to make the command device output silent
    * **ignore**: a list of devices names to ignore, by default is empty
    * **include**:  a list devices names to include, by default includes all.

    

------

### PARSER AND DECORATORS 

##### *Although more complex commands should be always stored in the device, sometimes they can be passed 'dynamically' from the host to the device*

These are some utils to send more complex commands to the device:

These complex commands include:

1. For/while loops with several level of indentation
2. Functions definitions

- #### For/while loops with several level of indentation:

  - **uparser_dec**: This is a function to parse loops inside a multiline string, and will return a command string ready to be sent

  - ```python
    >>> my_loop = """
    ... for i in range(10):
    ...     if True:
    ...         print('Hello World')
    ...     else:
    ...         pass
    ... """
    >>>
    >>> uparser_dec(my_loop)
    "for i in range(10):\rif True:\rprint('Hello World')\r\x08else:\rpass\r\r"
    >>> pyboard.cmd(uparser_dec(my_loop))
    for i in range(10):
    ...     if True:
    ...         print('Hello World')
    ...     else:
    ...         pass
    ...
    
    ...
    ...
    Hello World
    Hello World
    Hello World
    Hello World
    Hello World
    Hello World
    Hello World
    Hello World
    Hello World
    Hello World
    
    # Define a function that returns a for loop string 'command ready' that accepts parameters:
    
    >>> def test_loop(n, wait):
    ...     my_loop = """
    ...     for i in range({}):
    ...         for k in range(1,5):
    ...             pyb.LED(k).toggle()
    ...             time.sleep({})
    ...     """.format(n, wait)
    ...     return uparser_dec(my_loop)
    ...
    >>>
    >>> pyboard.cmd(test_loop(20, 0.05))
    for i in range(20):
    ...     for k in range(1,5):
    ...         pyb.LED(k).toggle()
    ...         time.sleep(0.05)
    ...
    >>>
    ```

- #### Functions definitions:

  - #### @upy_code:

    This decorator allows to define a function, that when is called, will return its source code as 'command ready' string. ** (This does not work in a Jupyter Notebook)

    ```python
    >>> @upy_code
    ... def test_loop(a):
    ...     for i in range(4):
    ...         print('led ON!')
    ...         led.on()
    ...         time.sleep(0.5)
    ...         print('led OFF!')
    
    ...         led.off()
    ...         time.sleep(0.5)
    ...     return [1,2,a]
    ...
    >>>
    >>> test_loop()
    @upy_code
    def test_loop(a):
        for i in range(4):
            print('led ON!')
            led.on()
            time.sleep(0.5)
            print('led OFF!')
            led.off()
            time.sleep(0.5)
        return [1,2,a]
    
    "def test_loop(a):\rfor i in range(4):\rprint('led ON!')\rled.on()\rtime.sleep(0.5)\rprint('led OFF!')\rled.off()\rtime.sleep(0.5)\r\x08return [1,2,a]\r\r"
    
    >>> pyboard.cmd(test_loop())
    @upy_code
    def test_loop(a):
        for i in range(4):
            print('led ON!')
            led.on()
            time.sleep(0.5)
            print('led OFF!')
            led.off()
    
            time.sleep(0.5)
        return [1,2,a]
    
    def test_loop(a):
    ...     for i in range(4):
    ...         print('led ON!')
    ...         led.on()
    ...         time.sleep(0.5)
    ...         print('led OFF!')
    ...         led.off()
    ...         time.sleep(0.5)
    ...     return [1,2,a]
    
    >>>>>> pyboard.cmd('test_loop(3)')
    led ON!
    led OFF!
    led ON!
    led OFF!
    led ON!
    led OFF!
    led ON!
    led OFF!
    [1, 2, 3]
    ```

- #### Python functions that are called in the device (where they were previously defined)

  - #### @upy_cmd(device, debug=False, rtn=True)

  ​	This allow a function that is defined in the device (passed as a parameter to the decorator), to be called as a python function. 

  * *Set debug to True if the function has print() statements or you want to catch an error*
  * *Set rtn to False if the function that is being called returns None* 
  
  ```python
  # A simple way to do this would be:
  def led_toggle(n_times, wait):
    pyboard.cmd('led_toggle({},{})'.format(n_times, wait))
    return pyboard.output
  
  # So when the function is called, it will send the command to execute the function with the defined parameters
  
  # A fancier way to do this would be the @upy_cmd decorator:
  
  @upy_cmd(device=pyboard)
  def led_toggle(n_times, wait):
    pass
  
  # And thats all, when led_toggle is called it will send the command to execute the function with the defined parameters
  
  # Example:
  # This function is already defined in the device:
  def test_f(n):
      return [1,n,3]
  
  # In python3 do:
  >>> @upy_cmd(device=pyboard)
  ... def test_f(n):
  ...     pass
  ...
  >>> test_f(10)
  [1, 10, 3]
  >>> result = test_f(10)
  >>> result
  [1, 10, 3]
  ```



- #### A Python 'Phantom' Class of a Class defined in MicroPython:

  - #### @upy_cmd_c(device, debug=False, rtn=True, out=False)

    This allows to define a 'phantom' class in python whose methods will call the methods of a defined class in MicroPython, see the next example with an IMU sensor and its library: (LSM9DS1)

    * *Set debug to True if the function has print() statements or you want to catch an error*
    * *Set rtn to False if the function that is being called returns None*
    * *Set out to True if the function that is being called in micropython is defined in the global space*



***IN MICROPYTHON:***
    

```python
>>> from lsm9ds1 import LSM9DS1
>>> from machine import I2C
>>> from machine import Pin
>>> i2c = I2C(scl=Pin(22), sda=Pin(23))
>>> imu = LSM9DS1(i2c)
>>> imu.read_accel()
(-0.03057861, -1.010193, 0.08703613)
>>> imu.read_gyro()
(-0.231781, 0.7177735, -0.3215027)
>>> imu.read_magnet()
(0.4556885, 0.2744141, -0.03625488)
```

***IN PYTHON3***

```python

# DEFINE THE DEVICE
from upydevice import W_UPYDEVICE, upy_cmd_c
esp32 = W_UPYDEVICE('192.168.1.53', 'mypass')

# DEFINE THE 'PHANTOM' CLASS

class LSM9DS1:
    def __init__(self, name): # must accept a name as a parameter
        """Phantom LSM9DS1 class"""
        self.name = name
        
    @upy_cmd_c(esp32)
    def read_gyro(self):
        return self.name # every method must return self.name
    @upy_cmd_c(esp32)
    def read_accel(self):
        return self.name
    @upy_cmd_c(esp32)
    def read_magnet(self):
        return self.name

imu = LSM9DS1(name='imu') # pass the name of the variable defined in MicroPython

# NOW CALLING THE METHODS, JUST CALLS THEM ON THE DEVICE

imu.read_accel()
(-0.0145874, -1.00061, 0.1412964)

imu.read_gyro()
(-0.4710389, 0.7925416, -0.3065491)

imu.read_magnet()
(0.456665, 0.2738037, -0.04858398)
```



- Pyboard example:

  - ```python
    # In MicroPython do:
    from pyb import LED
    
    # In Python3 do:
    from upydevice import PYBOARD, upy_cmd_c
    pyboard = PYBOARD('/dev/tty.usbmodem3370377430372')
    
    class LED:
        def __init__(self, number):
            """Phantom pyb.LED class"""
            self.name="{}({})".format('LED', number)
        
        @upy_cmd_c(pyboard, rtn=False)
        def toggle(self):
            return self.name
    
    green_led = LED(2)
    green_led.toggle()
    ```

    

- Another example, implement some uos Micropython methods

    - #### @upy_cmd_c_raw(device, out=False) 

      *Use this if the ouput of the function is not evaluable python object*

      ```python
      class UOS:
          def __init__(self):
            """Phantom UOS class"""
            self.name='uos'
         
          @upy_cmd_c(esp32)
          def listdir(self, directory):
            return self.name
      
      
          @upy_cmd_c_raw(esp32)
          def uname(self):
            return self.name
      
      uos = UOS()
      
      
      uos.listdir('/')
      ['boot.py', 'webrepl_cfg.py', 'main.py', 'lib']
      
      uos.uname()
      (sysname='esp32', nodename='esp32', release='1.11.0', version='v1.11-422-g98c2eabaf on 2019-10-11', machine='ESP32 module with ESP32')
      
      ```
    
  - #### Now we can do a custom ESP32 class that implements all these classes altogether:

```python

    class ESP32:
        def __init__(self, dev=esp32, sensor=imu, upy=uos):
            self.uos = upy
            self.d = dev
            self.imu = sensor
    
    my_esp32 = ESP32()
    
    my_esp32.imu.read_gyro()
    (-0.3663635, 0.814972, -0.4411316)
    
    my_esp32.uos.listdir('/')
    ['boot.py', 'webrepl_cfg.py', 'main.py', 'lib']
    
    my_esp32.uos.uname()
    (sysname='esp32', nodename='esp32', release='1.11.0', version='v1.11-422-g98c2eabaf on 2019-10-11', machine='ESP32 module with ESP32')
```

​    

- #### What about a reusable class ?

  Use **@upy_cmd_c_r**, **@upy_cmd_c_raw_r**, **@upy_cmd_c_r_in_callback**, **@upy_cmd_c_r_nb**, **@upy_cmd_c_r_nb_in_callback**.

  - #### @upy_cmd_c_r(debug=False, rtn=True, out=False) 

    - To call a 'standard' method of a defined class in MicroPython
  - *(Use out=True if the function is not a method of the Micropython class, eg: defined as an independent function)
  
- #### @upy_cmd_c_raw_r(out=False)
  
    - To call a method of a defined class in MicroPython whose output is not an evaluable python object
  
  - #### @upy_cmd_c_r_nb(debug=False, rtn=True, out=False)
  
    - Same as **@upy_cmd_c_r** but in 'non-blocking' mode. The use case is a function that returns None, or not returns anything. If used with a function that returns something, to get the output a call to *device.get_opt()* maybe needed before the output is stored and *device.output*.
  
  - #### @upy_cmd_c_r_in_callback(debug=False, rtn=True, out=False)
  
    - To call methods that accept function callbacks as a parameter, and the function callback is defined as a method of the MicroPython class.
  
  - #### @upy_cmd_c_r_nb_in_callback(debug=False, rtn=True, out=False)
  
    - Same as **@upy_cmd_c_r_in_callback** but in 'non-blocking' mode.
  
    Define a class like in the following example:
    
    ```python
    class UOS:
        def __init__(self, device):
            """Phantom UOS class"""
            self.name='uos'
            self.dev_dict = {'name':self.name, 'dev':device}
        @upy_cmd_c_r()
        def listdir(self, directory):
            return self.dev_dict
        
        
        @upy_cmd_c_raw_r()
        def uname(self):
            return self.dev_dict
    
    # Now it can be used with sereval devices:
    
    esp32_uos = UOS(esp32)
    
    esp32_uos.listdir('/')
    ['boot.py', 'webrepl_cfg.py', 'main.py', 'lib']
    
    pyb_uos = UOS(pyboard)
    
    pyb_uos.listdir('/flash')
    ['main.py', 'pybcdc.inf', 'README.txt', 'boot.py', '.fseventsd', 'udummy.py']
    
    ## And now the custom esp32 class would look like this:
    
    class ESP32:
        def __init__(self, dev=esp32):
            self.d= dev
            self.uos = UOS(self.d)
    
    
    my_esp32_custom = ESP32()
    
    my_esp32_custom.uos.listdir('/')
    ['boot.py', 'webrepl_cfg.py', 'main.py', 'lib']
    ```




- #### Another example: A 'phantom' Timer class

- ```python
  # In MicroPython do:
  from machine import Timer
  Tim = Timer(1)
  
  # # LED CALLBACK
  
  def led_toggle(x):
  	led.value(not led.value()) # led is already defined in esp32 Pin(13)
    
  # In Python3 do:
  
  class machine_Timer:
      def __init__(self, device, name):
          self.name = name
          self.dev_dict = {'name':self.name, 'dev':device}
          self.PERIODIC = 1
          self.ONE_SHOT = 0
      
      @upy_cmd_c_r(rtn=False)
      def init(self, mode, period, callback):
          return self.dev_dict
      
      @upy_cmd_c_r(rtn=False)
      def deinit(self):
          return self.dev_dict
  
  # NOW THE CALLBACK
  
  def led_toggle():
    pass
  
  # NOW EVERYTHIN IS READY
  esp32_timer = machine_Timer(esp32, name='Tim') # esp32 is an already defined W_UPYDEVICE
  
  esp32_timer.init(mode=esp32_timer.PERIODIC, period=500, callback=led_toggle)
  
  # now the led should blink every 500 millisecs
  # to stop it
  esp32_timer.deinit()
  ```



And finally, the complete ESP32 class with a custom function to start the blinking led:

```python
class ESP32:
    def __init__(self, dev=esp32):
        self.d= dev
        self.uos = UOS(self.d)
        self.machine = MACHINE(self.d)
        self.imu = LSM9DS1(self.d, name= 'imu')
        self.timer = machine_Timer(self.d, name='Tim')
    
    def start_blink(self, c_period):
        self.timer.init(mode=self.timer.PERIODIC, period=c_period, callback=self.led_toggle)
    
    def led_toggle(self):
        pass


t_esp32 = ESP32()
t_esp32.start_blink(500) # now the led should blink every 500 millisecs

# t_esp32.timer.deinit() to stop
```



------



### APP BUNDLE 

#### Making a stand alone app (with Pyinstaller)

To make a 'stand alone app' from a python script that uses uPydevice, some necessary steps must be done:

1. ##### Get the path of the 'bundle directory':

   To do this put the following code at the beginning of the script (see [Pyinstaller manual](https://pyinstaller.readthedocs.io/en/stable/))

   ```python
   import sys
   import os
   from upydevice import W_UPYDEVICE
   global bundle_dir
   frozen = 'not'
   if getattr(sys, 'frozen', False):
           # we are running in a bundle
           frozen = 'ever so'
           bundle_dir = sys._MEIPASS
   else:
           # we are running in a normal Python environment
           bundle_dir = os.path.dirname(os.path.abspath(__file__))
   
   # now the path is stored in bundle_dir variable
   ```

2. ##### Set the bundle_dir path in the device at creation:

   ```python
   esp32 = W_UPYDEVICE('192.168.1.67', 'mypass', bundle_dir=str(bundle_dir)+'/')
   ```

3. ##### Add the binaries when 'freezing the code' with the pyinstaller command

   ​	These binaries are:

   - 'web_repl_cmd_r': To send commands to a W_UPYDEVICE (add this binary if using a W_UPYDEVICE)

   - 'picocom': to send commands to a S_UPYDEVICE / PYBOARD (add this binary if using a S_UPYDEVICE / PYBOARD  )

     **These binaries are in the github repository under the [app_binaries](https://github.com/Carglglz/upydevice/blob/master/app_binaries) directory*

     **Clone the repository and put the binaries needed in the same folder as the 'python_app.py' script*

     Example: app that uses a W_UPYDEVICE:

```bash
$ pyinstaller my_python_app.py -w --add-data "web_repl_cmd_r:." -y -n my_python_app
```

​			Example: app that uses a S_UPYDEVICE:

```bash
$ pyinstaller my_python_app.py -w --add-data "picocom:." -y -n my_python_app
```
