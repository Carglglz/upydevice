# uPydevice

[![PyPI version](https://badge.fury.io/py/upydevice.svg)](https://badge.fury.io/py/upydevice)[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

Python library to interface with MicroPython devices through REPL:

-  Websockets/WebREPL (WiFi)
-  BleREPL (Bluetooth Low Energy)
-  Serial REPL (USB)

### Install
`pip install upydevice`  or `pip install --upgrade upydevice`

#### Example usage:

### ANY DEVICE: `Device`

This will return a Device based on address (first argument) type.

e.g.

```
>>> from upydevice import Device
>>> esp32_ws = Device('192.168.1.56', 'mypass', init=True, autodetect=True)
>>> esp32_ws
WebSocketDevice @ ws://192.168.1.53:8266, Type: esp32, Class: WebSocketDevice
Firmware: MicroPython v1.16 on 2021-06-19; ESP32 module with ESP32
(MAC: 30:ae:a4:23:35:64, RSSI: -43 dBm)
>>> esp32_sr = Device('/dev/tty.SLAB_USBtoUART', init=True)
>>> esp32_sr
SerialDevice @ /dev/tty.SLAB_USBtoUART, Type: esp32, Class: SerialDevice
Firmware: MicroPython v1.16 on 2021-06-19; ESP32 module with ESP32
CP2104 USB to UART Bridge Controller, Manufacturer: Silicon Labs
(MAC: 30:ae:a4:23:35:64)
>>> esp32_ble = Device('F53EDB2E-25A2-45A7-95A5-4D775DFE51D2', init=True)
>>> esp32_ble
BleDevice @ F53EDB2E-25A2-45A7-95A5-4D775DFE51D2, Type: esp32 , Class: BleDevice
Firmware: MicroPython v1.16 on 2021-06-19; ESP32 module with ESP32
(MAC: 30:ae:a4:23:35:64, Local Name: esp_ble, RSSI: -70 dBm)
```

### WIRELESS DEVICE (WebREPL Protocol): `WebSocketDevice`

This requires [WebREPL](http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi)  to be enabled in the device.

```
>>> from upydevice import WebSocketDevice
>>> esp32 = WebSocketDevice('192.168.1.56', 'mypass', init=True, autodetect=True)
>>> esp32.wr_cmd('led.on()')
>>> esp32.wr_cmd("uos.listdir()")
['boot.py', 'webrepl_cfg.py', 'main.py'] # this output is stored in [upydevice].output

>>> esp32.output
['boot.py', 'webrepl_cfg.py', 'main.py']
>>>> esp32.wr_cmd('x = [1,2,3];my_var = len(x);print(my_var)')
3
# Soft Reset:
>>> esp32.reset()
    Rebooting device...
    Done!
```

### BLE DEVICE (BleREPL Protocol): `BleDevice`

This requires [BleREPL](https://upydev.readthedocs.io/en/latest/gettingstarted.html) to be enabled in the device. (This is still experimental and performance may be platform and device dependent)

```
>>> from upydevice import BleDevice
>>> esp32 = BleDevice("9998175F-9A91-4CA2-B5EA-482AFC3453B9", init=True)
Device with address 9998175F-9A91-4CA2-B5EA-482AFC3453B9 was not found
Trying again...
Device with address 9998175F-9A91-4CA2-B5EA-482AFC3453B9 was not found
Trying again...
Connected to: 9998175F-9A91-4CA2-B5EA-482AFC3453B9
>>> esp32.wr_cmd('led.on()')
>>> esp32.wr_cmd("uos.listdir()")
['boot.py', 'webrepl_cfg.py', 'main.py', 'lib'] # this output is stored in [upydevice].output

>>> esp32.output
['boot.py', 'webrepl_cfg.py', 'main.py', 'lib']
>>> esp32.wr_cmd('x = [1,2,3];my_var = len(x);print(my_var)')
3

# Soft Reset:
>>> esp32.reset()
    Rebooting device...
    Done!
```



### SERIAL DEVICE (USB) : `SerialDevice`

Works for any serial device (esp, pyboard, circuitplayground...)

```
from upydevice import SerialDevice
>>> esp32 = SerialDevice('/dev/tty.SLAB_USBtoUART', autodetect=True) # baudrate default is 115200
>>> esp32.wr_cmd('led.on()')
>>> esp32.wr_cmd("uos.listdir()")
['boot.py', 'webrepl_cfg.py', 'main.py'] # this output is stored in [upydevice].output

>>> esp32.output
['boot.py', 'webrepl_cfg.py', 'main.py']
>>>> esp32.wr_cmd('x = [1,2,3];my_var = len(x);print(my_var)')
3
# Soft Reset:
>>> esp32.reset()
    Rebooting device...
    Done!
```

### Testing devices with Pytest:
Under `test` directory there are example tests to run with devices. This allows to test MicroPython code in devices interactively, e.g. button press, screen swipes, sensor calibration, actuators, servo/stepper/dc motors ...
e.g.
```
$ pytest test_esp_serial.py -s
```

### Made with upydevice:

- [upydev](https://github.com/Carglglz/upydev)
- [Jupyter_upydevice_kernel](https://github.com/Carglglz/jupyter_upydevice_kernel)

## More advanced examples:

### Phantom module

This module has some python 'phantom' classes to make easier the interaction with the same classes in the upydevice.

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
from upydevice import WebSocketDevice
from upydevice.phantom import UOS
esp32 = WebSocketDevice('192.168.1.73', 'mypass')
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
from upydevice import WebSocketDevice
esp32 = WebSocketDevice('192.168.1.73', 'mypass')
from upydevice.phantom import IMU_STREAMER
imu_st = IMU_STREAMER(esp32, name='imu_st', init_soc=True)
	192.168.1.43  # (This prints host ip)

# SIMPLE SAMPLE (this uses upydevice.cmd)
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

## [Examples (scripts, GUI ...)](https://github.com/Carglglz/upydevice/tree/develop/examples)
