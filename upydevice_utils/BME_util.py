# @Author: carlosgilgonzalez
# @Date:   2019-11-05T04:45:56+00:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-11-15T23:56:45+00:00


from machine import I2C, Pin
from STREAMER_util import U_STREAMER
from IRQ_util import U_IRQ_MG

try:
    i2c = I2C(scl=Pin(22), sda=Pin(23))
except ValueError:
    print('Non defualt I2C PINS')
    pass


class U_BME_IRQ(U_IRQ_MG):
    def __init__(self, my_bme_class, i2c):
        self.bme = my_bme_class(i2c=i2c)

    def read_data(self):
        return self.bme.read_compensated_data()


class U_BME_STREAMER(U_STREAMER):
    def __init__(self, bme_class, i2c, p_format='f', n_vars=3,
                 buffer_size=32):
        super().__init__(p_format=p_format, n_vars=n_vars,
                         buffer_size=buffer_size)
        self.i2c = i2c
        self.bme = bme_class(i2c=i2c)
        self.read_method = self.bme.read_compensated_data

    def read_data(self):
        return self.bme.read_compensated_data()
