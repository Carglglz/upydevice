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
