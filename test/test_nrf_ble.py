from upydevice import Device
import time
import logging
import sys
import upydev
import json
import os

_NRFDEV_BLE = 'F53EDB2E-25A2-45A7-95A5-4D775DFE51D2'
CHECK = '[\033[92m\u2714\x1b[0m]'
XF = '[\u001b[31;1m\u2718\u001b[0m]'

TOUCH_EVENTS = {5: 'Touch Event', 1: 'Swipe Event TOP-DOWN', 2: 'Swipe Event DOWN-TOP',
                4: 'Swipe Event LEFT-RIGHT', 3: 'Swipe Event RIGHT-LEFT'}


# Logging Setup

log_levels = {'debug': logging.DEBUG, 'info': logging.INFO,
              'warning': logging.WARNING, 'error': logging.ERROR,
              'critical': logging.CRITICAL}
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_levels['info'])
logging.basicConfig(
    level=log_levels['debug'],
    format="%(asctime)s [%(name)s] [%(threadName)s] [%(levelname)s] %(message)s",
    # format="%(asctime)s [%(name)s] [%(process)d] [%(threadName)s] [%(levelname)s]  %(message)s",
    handlers=[handler])
formatter = logging.Formatter(
    '%(asctime)s [%(name)s] [%(dev)s] [%(devp)s] : %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('pytest')

# INIT DEV


def test_devname(devname):
    global dev, log
    group_file = 'UPY_G'
    # print(group_file)
    if '{}.config'.format(group_file) not in os.listdir():
        group_file = '{}/{}'.format(upydev.__path__[0], group_file)
    with open('{}.config'.format(group_file), 'r', encoding='utf-8') as group:
        devices = json.loads(group.read())
        # print(devices)
    devs = devices.keys()
    # NAME ENTRY POINT
    if devname in devs:
        dev_uuid = devices[devname][0]
        dev_pass = devices[devname][1]
    else:
        if devname != 'default':
            # load upydev_.config
            file_conf = 'upydev_.config'
            if file_conf not in os.listdir():
                file_conf = os.path.join(upydev.__path__[0], 'upydev_.config')

            with open(file_conf, 'r') as config_file:
                upy_conf = json.loads(config_file.read())
                dev_uuid = upy_conf['uuid']
                dev_pass = upy_conf['passwd']

    if devname == 'default':
        dev = Device(_NRFDEV_BLE, init=True, autodetect=True, lenbuff=20)

    else:

        dev = Device(dev_uuid, init=True, autodetect=True, lenbuff=20)

    extra = {'dev': devname, 'devp': dev.dev_platform.upper()}
    log = logging.LoggerAdapter(log, extra)


def do_pass(test_name):
    log.info('{} TEST: {}'.format(test_name, CHECK))


def do_fail(test_name):
    log.error('{} TEST: {}'.format(test_name, XF))


def test_platform():
    TEST_NAME = 'DEV PLATFORM'
    try:
        log.info('Running BleDevice test...')
        log.info('DEV PLATFORM: {}'.format(dev.dev_platform))
        print(dev)
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


def test_button_press():
    TEST_NAME = 'BUTTON PRESS'
    log.info('{} TEST: Waiting for side button press'.format(TEST_NAME))
    dev.cmd('from flash.test_watch import *')
    time.sleep(0.2)
    print('Press side button now!')
    try:
        assert dev.cmd('button_press()', silent=True,
                       rtn_resp=True), 'Button press failed'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


def test_battery_charging():
    TEST_NAME = 'BATTERY CHARGING'
    log.info('{} TEST: Place the watch in the charging platform and connect it to power'.format(TEST_NAME))
    print('Waiting for charging state...')
    try:
        assert dev.cmd('battery_char()', silent=True,
                       rtn_resp=True), 'Battery not charging'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


def test_battery_level():
    TEST_NAME = 'BATTERY LEVEL'
    log.info('{} TEST: Check battery level > 5 %'.format(TEST_NAME))
    bat_lev = dev.cmd('battery_lev()', silent=True, rtn_resp=True)
    print('Battery Level: {} %'.format(bat_lev))
    try:
        assert bat_lev > 5, 'Battery level too low (under 5%)'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


def test_touch_event():
    TEST_NAME = 'TOUCH EVENT'
    log.info('{} TEST: Touch the display'.format(TEST_NAME))
    print('Waiting for a touch event...')
    try:
        t_event = dev.cmd('touch_event()', silent=True, rtn_resp=True)
        assert t_event, 'Touch event not received'
        print('{} received at X: {}, Y: {}'.format(TOUCH_EVENTS[t_event[0]],
                                                   t_event[1], t_event[2]))
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


def test_display_rgb_logo():
    TEST_NAME = 'DISPLAY RGB-LOGO'
    log.info('{} TEST: Display Red, Green, Blue, and finally MicroPython Logo'.format(TEST_NAME))
    print('Displaying RED ...')
    dev.cmd("display('red')", silent=True)
    time.sleep(1)
    print('Displaying GREEN ...')
    dev.cmd("display('green')", silent=True)
    time.sleep(1)
    print('Displaying BLUE ...')
    dev.cmd("display('blue')", silent=True)
    time.sleep(1)
    print('Displaying MicroPython logo...')
    dev.cmd("display('black')", silent=True)
    time.sleep(0.2)
    try:
        assert dev.cmd("display('logo')", silent=True,
                       rtn_resp=True), 'Display logo failed'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


def test_raise_device_exception():
    TEST_NAME = 'DEVICE EXCEPTION'
    log.info('{} TEST: b = 1/0'.format(TEST_NAME))
    try:
        assert not dev.cmd(
            'b = 1/0', rtn_resp=True), 'Device Exception: ZeroDivisionError'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


# def test_reset():
#     TEST_NAME = 'DEVICE RESET'
#     log.info('{} TEST'.format(TEST_NAME))
#     dev.reset()
#     try:
#         assert dev.connected, 'Device Not Connected'
#         do_pass(TEST_NAME)
#         print('Test Result: ', end='')
#     except Exception as e:
#         do_fail(TEST_NAME)
#         print('Test Result: ', end='')
#         raise e


def test_disconnect():
    TEST_NAME = 'DEVICE DISCONNECT'
    log.info('{} TEST'.format(TEST_NAME))
    try:
        dev.disconnect()
        assert not dev.connected, 'Device Still Connected'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e
