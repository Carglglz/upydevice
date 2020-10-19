#!/usr/bin/env python 3

# MIT License
#
# Copyright (c) 2020 Carlos Gil Gonzalez
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""upydevice dev tools"""

import os
import json

dev_dir = '.upydevices'
dev_path = "{}/{}".format(os.environ['HOME'], dev_dir)


def setup_devs_dir(debug=False, name_dir=dev_dir):
    if name_dir not in os.listdir("{}".format(os.environ['HOME'])):
        os.mkdir("{}/{}".format(os.environ['HOME'], name_dir))
        if debug:
            print('{} directory created in HOME:{} directory'.format(name_dir, os.environ['HOME']))


def store_dev(name, ip=None, passwd=None, s_port=None, dir=dev_path,
              debug=False, **kargs):
    dev_ip = ip
    dev_pass = passwd
    dev_s_port = s_port
    dev_conf = {'ip': dev_ip, 'passwd': dev_pass,
                's_port': dev_s_port}
    file_conf = '{}/{}.config'.format(dir, name)
    for key, val in kargs.items():
        if key not in dev_conf.keys():
            dev_conf[key] = val
    with open(file_conf, 'w') as config_file:
        config_file.write(json.dumps(dev_conf))
    if debug:
        print('device {} settings saved in {} directory!'.format(name, dir))


def load_dev(name, dir=dev_path, debug=False):
    try:
        file_conf = '{}/{}.config'.format(dir, name)
        with open(file_conf, 'r') as config_file:
            dev_conf = json.loads(config_file.read())
        return dev_conf
    except Exception as e:
        if debug:
            print("CONFIGURATION FILE NOT FOUND")
        return None
