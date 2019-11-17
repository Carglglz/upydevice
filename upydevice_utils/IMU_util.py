# @Author: carlosgilgonzalez
# @Date:   2019-11-05T04:43:41+00:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-11-15T23:09:32+00:00


from machine import I2C, Pin
import json
from array import array
from STREAMER_util import U_STREAMER
from IRQ_util import U_IRQ_MG

try:
    i2c = I2C(scl=Pin(22), sda=Pin(23))
except ValueError:
    print('Non defualt I2C PINS')
    pass


# IRQ

class U_IMU_IRQ(U_IRQ_MG):
    def __init__(self, imu_lib, i2c, sig_pin, irq_pin, opt='acc', n_vars=3,
                 p_format='f', timeout=1000):  # SUPER INIT IRQ_UTIL
        super().__init__(sig_pin, irq_pin, timeout=timeout)
        self.imu = imu_lib(i2c)
        self.opt = opt
        self.buff = array('f', (0 for _ in range(3)))
        if self.opt == 'acc':
            self.read_method = self.imu.read_accel
        if self.opt == 'gyro':
            self.read_method = self.imu.read_gyro
        if self.opt == 'mag':
            self.read_method = self.imu.read_magnet

    def read_data(self):
            self.buff[0], self.buff[1], self.buff[2] = self.read_method()
            return self.buff

    def set_mode(self, mode):
        self.opt = mode
        if self.opt == 'acc':
            self.read_method = self.imu.read_accel
        if self.opt == 'gyro':
            self.read_method = self.imu.read_gyro
        if self.opt == 'mag':
            self.read_method = self.imu.read_magnet
        return self.opt


# STREAMER

class U_IMU_STREAMER(U_STREAMER):
    def __init__(self, imu_lib, i2c, opt='acc', p_format='f', n_vars=3,
                 buffer_size=32, max_digit=8):
        super().__init__(p_format=p_format, n_vars=n_vars,
                         buffer_size=buffer_size)
        self.i2c = i2c
        self.opt = opt
        self.imu = imu_lib(i2c)
        self.data_x = array("f", (0 for _ in range(self.BUFFERSIZE)))
        self.data_y = array("f", (0 for _ in range(self.BUFFERSIZE)))
        self.data_z = array("f", (0 for _ in range(self.BUFFERSIZE)))
        self.variables = ['X', 'Y', 'Z']
        self.max_dig = max_digit
        if self.opt == 'acc':
            self.read_method = self.imu.read_accel
        if self.opt == 'gyro':
            self.read_method = self.imu.read_gyro
        if self.opt == 'mag':
            self.read_method = self.imu.read_magnet

    def read_data(self):
            self.buff[0], self.buff[1], self.buff[2] = self.read_method()
            return self.buff

    def set_mode(self, mode):
        self.opt = mode
        if self.opt == 'acc':
            self.read_method = self.imu.read_accel
        if self.opt == 'gyro':
            self.read_method = self.imu.read_gyro
        if self.opt == 'mag':
            self.read_method = self.imu.read_magnet

    def max_digit(self, data):
        return [float(str(val)[:self.max_dig]) for val in data]

    def chunk_send_json(self, x):
        if self.irq_busy:
            return
        try:
            self.irq_busy = True
            if self.index_put < self.BUFFERSIZE:
                self.data_x[self.index_put], self.data_y[self.index_put], self.data_z[self.index_put] = self.read_method()
                self.index_put += 1
            elif self.index_put == self.BUFFERSIZE:
                self.cli_soc.sendall(json.dumps(dict(zip(self.variables, [list(self.data_x), list(self.data_y), list(self.data_z)]))))
                self.index_put = 0
            self.irq_busy = False
        except Exception as e:
            self.irq_busy = False
