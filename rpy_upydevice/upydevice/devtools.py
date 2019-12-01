#!/usr/bin/env python 3
# @Author: carlosgilgonzalez
# @Date:   2019-11-16T00:31:56+00:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-11-16T01:26:58+00:00

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
