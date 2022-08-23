# uPydevice

[![PyPI version](https://badge.fury.io/py/upydevice.svg)](https://badge.fury.io/py/upydevice)[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

Python library to interface with MicroPython devices through REPL*:

- Websockets/WebREPL (WiFi)
- BleREPL (Bluetooth Low Energy)
- Serial REPL (USB)

\*  *Device REPL must be accesible.*

Upydevice allows to integrate device interaction from simple scripts to automated services,  test suites, command line interfaces or even GUI applications.

### Install

`pip install upydevice`  or `pip install --upgrade upydevice`

#### Example usage:

### DEVICE: `Device`

```python
>>> from upydevice import Device
```

This will return a Device based on address (first argument) type.

e.g.

### Serial (USB)

```python
>>> esp32 = Device('/dev/cu.usbserial-016418E3', init=True)
>>> esp32
SerialDevice @ /dev/cu.usbserial-016418E3, Type: esp32, Class: SerialDevice
Firmware: MicroPython v1.19.1-285-gc4e3ed964-dirty on 2022-08-12; ESP32 module with ESP32
CP2104 USB to UART Bridge Controller, Manufacturer: Silicon Labs
(MAC: 30:ae:a4:23:35:64)
```

### WiFi (WebSockets/WebREPL)

This requires [WebREPL](http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi) to be enabled in the device.

```python
>>> esp32 = Device('192.168.1.53', 'mypass', init=True)
>>> esp32
WebSocketDevice @ ws://192.168.1.53:8266, Type: esp32, Class: WebSocketDevice
Firmware: MicroPython v1.19.1-285-gc4e3ed964-dirty on 2022-08-12; ESP32 module with ESP32
(MAC: 30:ae:a4:23:35:64, Host Name: espdev, RSSI: -45 dBm)
```

If device hostname name is set e.g. (in device `main.py`)

```python
....
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(hostname='espdev')
wlan.connect('your-ssid', 'your-key')
...
```

Now the device can be connected with mDNS name.

```python
>>> esp32 = Device('espdev.local', 'mypass', init=True)
>>> esp32
WebSocketDevice @ ws://192.168.1.53:8266, Type: esp32, Class: WebSocketDevice
Firmware: MicroPython v1.19.1-285-gc4e3ed964-dirty on 2022-08-12; ESP32 module with ESP32
(MAC: 30:ae:a4:23:35:64, Host Name: espdev, RSSI: -45 dBm)
```

### BLE (BleREPL)

This requires [BleREPL](https://upydev.readthedocs.io/en/latest/gettingstarted.html) to be enabled in the device. (This is still experimental and performance may be platform and device dependent)

```python
>>> esp32 = Device('00FEFE2D-5983-4D6C-9679-01F732CBA9D9', init=True)
>>> esp32
BleDevice @ 00FEFE2D-5983-4D6C-9679-01F732CBA9D9, Type: esp32 , Class: BleDevice
Firmware: MicroPython v1.18-128-g2ea21abae-dirty on 2022-02-19; 4MB/OTA BLE module with ESP32
(MAC: ec:94:cb:54:8e:14, Local Name: espble, RSSI: -38 dBm)
```

Now the device can recive commands and send back the output. e.g.

```python
>>> esp32.wr_cmd('led.on()')
>>> esp32.wr_cmd("os.listdir()")
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

```python
$ pytest test_esp_serial.py -s

=========================================== test session starts ===========================================
platform darwin -- Python 3.7.9, pytest-7.1.2, pluggy-1.0.0
benchmark: 3.4.1 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /Users/carlosgilgonzalez/Desktop/IBM_PROJECTS/MICROPYTHON/TOOLS/upydevice_.nosync/test, configfile: pytest.ini
plugins: benchmark-3.4.1
collected 7 items

test_esp_serial.py::test_devname PASSED                                                             [ 14%]
test_esp_serial.py::test_platform
---------------------------------------------- live log call ----------------------------------------------
00:13:26 [pytest] [sdev] [ESP32] : Running SerialDevice test...
00:13:26 [pytest] [sdev] [ESP32] : DEV PLATFORM: esp32
00:13:26 [pytest] [sdev] [ESP32] : DEV PLATFORM TEST: [✔]
PASSED                                                                                              [ 28%]
test_esp_serial.py::test_blink_led
---------------------------------------------- live log call ----------------------------------------------
00:13:28 [pytest] [sdev] [ESP32] : BLINK LED TEST: [✔]
PASSED                                                                                              [ 42%]
test_esp_serial.py::test_run_script
---------------------------------------------- live log call ----------------------------------------------
00:13:28 [pytest] [sdev] [ESP32] : RUN SCRIPT TEST: test_code.py
00:13:31 [pytest] [sdev] [ESP32] : RUN SCRIPT TEST: [✔]
PASSED                                                                                              [ 57%]
test_esp_serial.py::test_raise_device_exception
---------------------------------------------- live log call ----------------------------------------------
00:13:31 [pytest] [sdev] [ESP32] : DEVICE EXCEPTION TEST: b = 1/0
00:13:31 [pytest] [sdev] [ESP32] : DEVICE EXCEPTION TEST: [✔]
PASSED                                                                                              [ 71%]
test_esp_serial.py::test_reset
---------------------------------------------- live log call ----------------------------------------------
00:13:31 [pytest] [sdev] [ESP32] : DEVICE RESET TEST
00:13:32 [pytest] [sdev] [ESP32] : DEVICE RESET TEST: [✔]
PASSED                                                                                              [ 85%]
test_esp_serial.py::test_disconnect
---------------------------------------------- live log call ----------------------------------------------
00:13:32 [pytest] [sdev] [ESP32] : DEVICE DISCONNECT TEST
00:13:32 [pytest] [sdev] [ESP32] : DEVICE DISCONNECT TEST: [✔]
PASSED                                                                                              [100%]

============================================ 7 passed in 6.74s ============================================
```

### Made with upydevice:

- [upydev](https://github.com/Carglglz/upydev)
- [Jupyter_upydevice_kernel](https://github.com/Carglglz/jupyter_upydevice_kernel)

## [Examples (scripts, GUI ...)](https://github.com/Carglglz/upydevice/tree/develop/examples)
