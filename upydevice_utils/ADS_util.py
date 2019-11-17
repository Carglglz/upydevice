#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-11-05T04:40:29+00:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-11-15T23:55:26+00:00


from machine import I2C, Pin
import time
from array import array
from STREAMER_util import U_STREAMER
from IRQ_util import U_IRQ_MG


try:
    i2c = I2C(scl=Pin(22), sda=Pin(23))
except ValueError:
    print('Non defualt I2C PINS')
    pass


class U_ADS_IRQ(U_IRQ_MG):
    def __init__(self, ads_lib, i2c, channel=0):
        self.addr = 72
        self.i2c = i2c
        self.range_dict = {0: 6.144, 1: 4.096, 2: 2.048, 3: 1.024, 4: 0.512,
                           5: 0.256}
        self.gain_dict = {0: 'x2/3', 1: 'x1', 2: 'x2', 3: 'x4', 4: 'x8',
                          5: 'x16'}
        self.gain = 1
        self.ads = ads_lib(self.i2c, self.addr, self.gain)
        self.channel = channel
        self.buff = array('f', (0 for _ in range(1)))
        time.sleep(1)
        self.ads.set_conv(7, channel1=self.channel)
        self.read_method = self.read_data_raw
        self.configuration = 'Channel: A{} | Voltage Range: +/- {} V | Gain: {} V/V'.format(
            self.channel, self.range_dict[self.gain], self.gain_dict[self.gain])

    def read_raw(self):
        self.buff[0] = self.ads.raw_to_v(self.ads.alert_read())
        return self.buff

    def read_data(self):
        for i in range(4):
            self.buff[0] = self.ads.read_rev()
        self.buff[0] = self.ads.raw_to_v(self.ads.read_rev())
        return self.buff


class U_ADS_STREAMER(U_STREAMER):
    def __init__(self, ads_lib, i2c, channel=0, p_format='f', n_vars=1,
                 buffer_size=20):
        super().__init__(p_format=p_format, n_vars=n_vars,
                         buffer_size=buffer_size)

        self.addr = 72
        self.range_dict = {0: 6.144, 1: 4.096, 2: 2.048, 3: 1.024, 4: 0.512,
                           5: 0.256}
        self.gain_dict = {0: 'x2/3', 1: 'x1', 2: 'x2', 3: 'x4', 4: 'x8',
                          5: 'x16'}
        self.gain = 1
        self.i2c = i2c
        self.channel = channel
        self.ads = ads_lib(self.i2c, self.addr, self.gain)
        time.sleep(1)
        self.ads.set_conv(7, channel1=self.channel)
        self.read_method = self.read_data_raw
        self.configuration = 'Channel: A{} | Voltage Range: +/- {} V | Gain: {} V/V'.format(
            self.channel, self.range_dict[self.gain], self.gain_dict[self.gain])

    def read_data(self):
        self.buff[0] = self.ads.raw_to_v(self.ads.alert_read())
        return self.buff

    def read_data_raw(self):
        self.buff[0] = self.ads.alert_read()
        return self.buff

    def read_shot(self):
        for i in range(4):
            self.buff[0] = self.ads.read_rev()
        self.buff[0] = self.ads.raw_to_v(self.ads.read_rev())
        return self.buff

    def init_ads_call(self):  # on_init callback
        self.ads.conversion_start(7, channel1=self.channel)

    def init_ads(self):  # on_init callback
        self.ads.conversion_start(7, channel1=self.channel)

    def set_channel(self, channel):
        self.channel = channel

    def set_mode(self, mode):
        if mode == 'stream':
            self.read_method = self.read_data
        elif mode == 'shot':
            self.read_method = self.read_shot
        elif mode == 'stream_raw':
            self.read_method = self.read_data_raw
