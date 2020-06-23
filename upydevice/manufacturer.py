#!/usr/bin/env python

import csv
import upydevice

with open('{}/manufacturer.csv'.format(upydevice.__path__[0]), 'r') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=['Dec', 'Hex', 'Company'])
    manufacturer_dict = {'Dec': [], 'Company': []}
    for row in reader:
        # print(row['Dec'], row['Hex'], row['Company'])
        manufacturer_dict['Dec'].append(int(row['Dec']))
        manufacturer_dict['Company'].append(row['Company'])

ble_manufacturer_dict = dict(zip(manufacturer_dict['Dec'], manufacturer_dict['Company']))
ble_manufacturer_dict_rev = dict(zip(manufacturer_dict['Company'], manufacturer_dict['Dec']))
