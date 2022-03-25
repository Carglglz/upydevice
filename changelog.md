# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [0.3.7] Unreleased Github Repo [develop]
## [0.3.6] - 2022-03-25
### Fix
- fixed missing dependencies in `setup.py` (@BradenM)
## [0.3.5] - 2022-03-15
### Fix
- reassign ip to hostname if hostname is not None for disconnect method
## [0.3.4] - 2022-03-04
### Fix
- `WebSocketDevice` double unwanted `super().__init__` bug.
- Load time in MacOS caused by bleak/corebluetooth, only if BleDevice
- Allow mdns `.local` name in WebSecureREPL, (ssl checkhostname / auth server.)
- `WebSocketDevice` receive frame errors
- `SerialDevice` follow command parsing errors
- `BleDevice` follow command parsing errors
- `is_reachable` method for `WebSocketDevice` if ip is mdns .local name
- pipe option for `BleDevice` `wr_cmd` method.
### Added
- Indicate websocket port in ip address as `ip:port` format
- Allow `password:passphrase` format for `WebSocketDevice` password that sets ssl/auth
to `True` if present.
- `address` property for all device types.
- `flush_conn` for `BleDevice` for compatibility
## [0.3.3] 2021-12-16
### Added
- `Host Name` in `__repr__` command device info
## [0.3.2] 2021-10-24
### Added
- mDNS `.local`/`dhcp_hostname` compatibility, so device configuration works across networks
### Fix
- `check -i`, `info` commands in `-apmd`, if connected to AP of the device.
## [0.3.1] - 2021-09-09
### Fix
- KeyboardInterrupt in AsyncBleDevice for jupyter_upydevice_kernel
## [0.3.0] - 2021-08-12
#### Bump to version 0.3.0
### Added
- Tests with `pytest` tested with esp32 (websocket, serial, ble), esp8266(websocket, serial), pyboard (serial) and nrf52832 (colmi p8 with wasp-os) (ble)
- `Device` function that returns Device class based on address type
- Pytest with devices
- `__repr__` that returns device info
- Raise `DeviceException` on raised Exception in device
- Raise `DeviceNotFound` after connection attempt fail or if device is not reachable.
- `ble_scan`, `net_scan`, `serial_scan`, to scan for devices
### Fix
- Base code refactoring
## [0.2.3] - 2020-05-25
### Added
- `BLE_DEVICE` for bluetooth low energy devices
### Fix
- Serial device `is_reachable` method fix
## [0.2.2] - 2020-02-24
### Fix
- WS_DEVICE cmd_nb fix for cmd method
## [0.2.1] - 2020-02-17
### Fix
- WS_DEVICE now works with esp8266 too.
## [0.2.0] - 2020-02-16
### Added
- NEW WS_DEVICE and SERIAL_DEVICE work in progress
## [0.1.9] - 2020-02-08
### Added
- BASE_WS_DEVICE compatibility with WebSecureREPL

## [0.1.8] - 2020-02-02
### Added
- BASE_SERIAL_DEVICE and BASE_WS_DEVICE work in progress
## [0.1.7] - 2020-01-19
### Fix
- W_UPYDEVICE kbi command can filter MicroPython banner info now
## [0.1.6] - 2020-01-10
### Added
- Reset option in "init" S_UPYDEVICE for upydev 'sh_srepl' compatibility
## [0.1.5] - 2020-01-07
### Added
- phantom_wr module like phantom but faster
### Fix
- KeyboardInterrupt handling in wr_cmd method of W_UPYDEVICE, S_UPYDEVICE, PYBOARD
## [0.1.4] - 2019-12-24
### Added
- New methods 'open_wconn', 'wr_cmd' and 'close_wconn' to open a wrepl session
and send commands (this will open a WebREPL connection and wont close it until
close_wconn is called, which means the other commands methods won't work) This
will drop the delay between sending a command and executing that command on the
device
- Methods 'open_wconn', 'wr_cmd' and 'close_wconn' for serial devices too.
(With serial REPL instead of WebREPL)
### Fix
- uparser_dec improved
## [0.1.3] - 2019-11-23
### Added
- Methods to UOS phantom class (mkdir, rmdir, getcwd, chdir, remove)
- Phantom pyb_Servo pyboard class
- New sensors IRQ phantom classes
## [0.1.2] - 2019-11-12
### Added
- New decorator (upy_cmd_c_r_in_callback) to be able to pass self methods (functions) as keywords arguments (for callbacks)
- New decorator that allows non-blocking function calls (upy_cmd_c_r_nb)
- New "IRQ_util.py" upy script (U_IRQ_MG class) + "Phantom" python IRQ_MG class
  This allow to manage/set interrupts, and receive and interrupt callback on python3 (see Phantom class Docs)
- New W_UPYDEVICE method 'is_reachable' (pings the device to see if it is
  reachable)
- New decorator (upy_cmd_c_r_nb_in_callback) to be able to pass self methods (functions) as keywords arguments (for callbacks) in non-blocking style
(good for timer interrupts)
- New "STREAMER_util.py" upy script (U_STREAMER class) as a "super" class to
  make streaming sensor data in real time easier (up to ~900 Hz of sampling frequency tested) + "Phantom" python STREAMER class (see Phantom class Docs)
- New phantom sensors classes (ADS1115, BME280, LSM9DS1)
- New phantom sensors STREAMER classes (IMU_STREAMER, BME_STREAMER,
  ADS_STREAMER)+ upydevice_utils scripts (IMU_util.py, ADS_util.py,
  BME_util.py) to test U_STREAMER and U_IRQ_MG classes (more about this in docs
  and examples)
## [0.1.1] - 2019-11-02
### Added
- phantom submodule, with some phantom classes (UOS, LSM9DS1, MACHINE, pyb_LED, pyb_Timer, machine_Timer, WLAN, AP, I2C)
- Now bytearray and array objects are supported

## [0.1.0] - 2019-10-29
### Added
- Now 'phantom' class methods allow to pass function in kwargs, this is useful to pass function to callbacks (for example Timers)
- option 'out' in class decorators that allows implement a function defined in micropython global space (main or dir()) as a part of a 'phantom' class

## [0.0.9] - 2019-10-28
### Added
- decorators for reusable 'phantom' classes
## [0.0.8] - 2019-10-28
### Fix
- decorators return option for commands that should return None
## [0.0.7] - 2019-10-28
### Added
- decorators for methods of 'phantom' python3 class

## [0.0.6] - 2019-10-27
### Added
- Non-blocking cmd_nb method
- methods and decorators to parse for/while loops and functions
- decorator to define a function as a shortcut to a function in MicroPython

## [0.0.5] - 2019-10-21
### Added
- GROUP class to send commands to a group of devices (one at a time or parallel)
- Name option parameter, and automatic naming (to make easier manage groups)
- 'Group silent' parameter and 'device silent' parameter to silence output
- Group output attribute, that catches the output of a group command and makes a dictionary like {device_1 :output_1, ..., device_n:output_n}
- Custom path indication with bundle_dir parameter at group creation (then no need to further indicate in cmd method)

## [0.0.4] - 2019-10-14
### Added
- Custom path indication with bundle_dir option in cmd method to indicate the path to the picocom binary for app development (command line or standalone) (For serial devices)

## [0.0.3] - 2019-09-28
### Added
- Silent option
- Custom path indication with bundle_dir option in cmd method to indicate the path to the web_repl_cmd_r binary for app development (command line or standalone) (For wireless devices)

## [0.0.2] - 2019-08-28
### Fix
- PYBOARD class commands output


## [0.0.1] - 2019-08-16
### Added
- First release
