# uPydevice

Python library to interface with Micropython devices through WebREPL protocol or through Serial connection.

### Requirements
* [upydev](https://github.com/Carglglz/upydev)
* [picocom](https://github.com/npat-efault/picocom)
* [pyserial](https://github.com/pyserial/pyserial/)
* [dill](https://github.com/uqfoundation/dill)
* [pexpect](https://github.com/pexpect/pexpect)

*upydev , pyserial and dill will be automatically installed with pip*  

*to install picocom do:*  `brew install picocom`

### Tested on

- OS: 
  - MacOS Mojave 10.14.6
  - Raspbian Stretch (9.11) (RPY ZERO W) (*just WebREPL protocol)
- BOARDS:
  - Esp32 (Adafruit feather Huzzah)
  - Esp8266 (Adafruit feather Huzzah)
  - Pyboard Little
  - Pyboard v1.1
  - CircuitPlayground Express

### Install
`pip install upydevice`

*To install in a raspberry pi do:*

`sudo apt-get install picocom`

*Install upydev manually as indicated in upydev README then*

```
$ git clone https://github.com/Carglglz/upydevice.git
$ cd upydevice/rpy_upydevice
$ sudo pip3 install . --no deps
[...]
$ sudo pip3 install pyserial
$ sudo pip3 install dill
```

#### Documentation:

See [DOCS](https://github.com/Carglglz/upydevice/blob/master/DOCS/Documentation.md)

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
        >>> pyboard.cmd('pyb.LED(1).toggle()', timeout=100)
    
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

### GROUP (to send commands to several devices at a time)

```
# Setup and configurate the devices :
    >>> from upydevice import W_UPYDEVICE, PYBOARD, GROUP
# PYBOARD
    >>> pyboard = PYBOARD('/dev/tty.usbmodem387E386731342')
# ESP32
    >>> esp32_A = W_UPYDEVICE('192.168.1.73', 'mypass')
    >>> esp32_B = W_UPYDEVICE('192.168.1.44', 'mypass')

# Setup and configurate the group:
    >>> my_group = GROUP([esp32_A, esp32_B, pyboard])

# Each upydevice has a name attribute that can be set at creation momment or after
# pyboard = PYBOARD('/dev/tty.usbmodem387E386731342', name='my_pyboard_1'); or pyboard.name = 'my_pyboard_1')
# If not set an automatic name will be set as 'upydev_class'+'ip or serial port'

# Send command:
    >>> my_group.cmd('import machine;import  ubinascii;ubinascii.hexlify(machine.unique_id())')
    Sending command to wupydev_73
    b'30aea4233564'

    Sending command to wupydev_44
    b'807d3a809b30'

    Sending command to pyboard_tty.usbmodem387E386731342
    b'33004e000351343134383038'

# There is an option to silent the group messages with group_silent = True, and or each device ouput with device_silent=True

# Output is stored in group output attribute:
    >>> my_group.output
    {'wupydev_73': b'30aea4233564', 'wupydev_44': b'807d3a809b30', 'pyboard_tty.usbmodem387E386731342': b'33004e000351343134383038'}

# Send command parallel mode **: (experimental mode, may not work 100% of the times, depends on the connection quality (for wireless devices))
    >>> my_group.cmd_p('6*12')
    Sending command to: wupydev_73, wupydev_44, pyboard_tty.usbmodem387E386731342
    72


    72

    72

    Done!
# To see which ouput corresponds to which device use 'id=True' parameter:

    >>> my_group.cmd_p('ubinascii.hexlify(machine.unique_id())', id=True)
    Sending command to: wupydev_73, wupydev_44, pyboard_tty.usbmodem387E386731342
    pyboard_tty.usbmodem387E386731342:b'33004e000351343134383038'
    pyboard_tty.usbmodem387E386731342:
    pyboard_tty.usbmodem387E386731342:
    wupydev_44:b'807d3a809b30'
    wupydev_73:b'30aea4233564'
    wupydev_44:
    wupydev_73:
    Done!
    >>>
    >>> my_group.output
    {'wupydev_73': b'30aea4233564', 'wupydev_44': b'807d3a809b30', 'pyboard_tty.usbmodem387E386731342': b'33004e000351343134383038'}
```



## More advanced examples:

### Phantom module

This module has some python 'phantom' classes to make easier the interaction with the same classes in the upydevice. These classes are made using a series of decorators described in [DOCS](https://github.com/Carglglz/upydevice/blob/master/DOCS/Documentation.md#PARSER-AND-DECORATORS) 

Available classes:

* MicroPython classes:
  * **MACHINE** (just unique_id() method)
  * **Pin**
  * **I2C**
  * **UOS**
  * **pyb_LED**
  * **pyb_Timer**
  * **pyb_Servo**
  * **machine_Timer**
  * **WLAN**
  * **AP**
* Sensor classes:
  * **LSM9DS1**
  * **BME280**
  * **ADS1115**
* Custom classes:
  * **IRQ_MG** (This needs *IRQ_util.py in the micropython device*)
  * **STREAMER** (to use as a super class, and this needs *STREAMER_util.py in the micropython device*)
  * **IMU_STREAMER**  (This needs *IMU_util.py in the micropython device*)
  * **BME_STREAMER** (This needs *BME_util.py in the micropython device*)
  * **ADS_STREAMER**  (This needs *ADS_util.py in the micropython device*)

Examples:

**UOS**

```
from upydevice import W_UPYDEVICE
from upydevice.phantom import UOS
esp32 = W_UPYDEVICE('192.168.1.73', 'mypass')
uos = UOS(esp32)
uos.listdir('/')
 ['boot.py', 'webrepl_cfg.py', 'main.py']
uos.uname()
 (sysname='esp32', nodename='esp32', release='1.11.0', version='v1.11-530-g25946d1ef on 2019-10-29', machine='ESP32 module with ESP32')
```



## Upydevice_utils

These are some useful modules to put in the micropython device:

* **IRQ_util.py** : A module to test/setup hardware interrupts easily
* **STREAMER_util.py**: A module with U_STREAMER 'super' class to make streaming sensor data in real time easily.
* **IMU_util.py**: A module with U_IMU_IRQ and U_IMU_STREAMER example classes.
* **BME_util.py**: A module with U_BME_IRQ and U_BME_STREAMER example classes.
* **ADS_util.py**: A module with U_ADS_IRQ and U_ADS_STREAMER example classes.



Example: *phantom IMU_STREAMER + U_IMU_STREAMER classes*

*In MicroPython*

```
from IMU_util import i2c, U_IMU_STREAMER
from lsm9ds1 import LSM9DS1
imu_st = U_IMU_STREAMER(LSM9DS1, i2c)
```

*Now the device is ready to be controlled from Python3*

*In Python3*

```
from upydevice import W_UPYDEVICE
esp32 = W_UPYDEVICE('192.168.1.73', 'mypass')
from upydevice.phantom import IMU_STREAMER
imu_st = IMU_STREAMER(esp32, name='imu_st', init_soc=True)
	192.168.1.43  # (This prints host ip)

# SIMPLE SAMPLE (this use upydevice.cmd)
imu_st.read_data()
	array('f', [-0.4462279975414276, -0.12023930251598358, -0.9497069716453552])
imu_st.setup_mode('gyro')
imu_st.read_data()
	array('f', [-0.007476807106286287, 0.9719849824905396, -0.0971985012292862])
imu_st.setup_mode('mag')
imu_st.read_data()
	array('f', [0.4848633110523224, 0.1734618991613388, 0.2396239936351776])
imu_st.setup_mode('acc')
imu_st.read_data()
	array('f', [-0.4470824897289276, -0.12023930251598358, -0.9493408203125])

# SOCKETS
imu_st.start_server()
	Server listening...
	Connection received from: 192.168.1.73:50185
imu_st.shot_read(imu_st.data_print, timeout=1)
	X: -0.44537353515625, Y: -0.12030029296875, Z: -0.94879150390625 (g=-9.8m/s^2)

# CONTINUOUS STREAMING THROUGH SOCKETS + TEST

imu_st.continuous_stream(imu_st.data_print_static, timeout=10, static=True, test=True)
	Streaming IMU ACCELEROMETER: X, Y, Z (g=-9.8m/s^2),fq=100.0Hz


       X              Y              Z
^C  -0.4431        -0.1184        -0.9482

	Flushed!
	Done!

imu_st.get_stream_test()
  STREAM TEST RESULTS ARE:
  TEST DURATION : 11.31895899772644 (s)
  DATA PACKETS : 1077 packets
  SAMPLES PER PACKET : 1
  VARIABLES PER SAMPLE : 3; ['X', 'Y', 'Z']
  SIZE OF PACKETS: 12 bytes
  Period: 10 ms ; Fs:100.0 Hz, Data send rate: 95 packets/s of 1 samples
  DATA TRANSFER RATE (kBps): 1.11328125 kB/s
  DATA TRANSFER RATE (Mbps): 0.00890625 Mbps

imu_st.stop_server()
```

