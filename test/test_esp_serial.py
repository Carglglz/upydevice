from upydevice import Device
import time
import logging
import sys
import json
import upydev
import os

_ESPDEV_SERIAL = '/dev/tty.SLAB_USBtoUART'
CHECK = '[\033[92m\u2714\x1b[0m]'
XF = '[\u001b[31;1m\u2718\u001b[0m]'

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
formatter = logging.Formatter('%(asctime)s [%(name)s] [%(dev)s] : %(message)s')
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
        dev_baud = devices[devname][0]
        dev_port = devices[devname][1]

    if devname == 'default':
        dev = Device(_ESPDEV_SERIAL, init=True, autodetect=True)

    else:
        dev = Device(dev_port, baudrate=dev_baud, init=True, autodetect=True)

    extra = {'dev': dev.dev_platform.upper()}
    log = logging.LoggerAdapter(log, extra)


def do_pass(test_name):
    log.info('{} TEST: {}'.format(test_name, CHECK))


def do_fail(test_name):
    log.error('{} TEST: {}'.format(test_name, XF))


# BLINK TEST
_ESP_LED = 13


def test_platform():
    log.info('Running SerialDevice test...')
    log.info('DEV PLATFORM: {}'.format(dev.dev_platform))
    print(dev)
    print('Test Result: ', end='')


def test_blink_led():
    TEST_NAME = 'BLINK LED'
    dev.cmd('from machine import Pin; led = Pin({}, Pin.OUT)'.format(_ESP_LED))
    for i in range(2):
        dev.cmd('led.on();print("LED: ON")')
        time.sleep(0.2)
        dev.cmd('led.off();print("LED: OFF")')
        time.sleep(0.2)
    try:
        assert dev.cmd('not led.value()', silent=True, rtn_resp=True), 'LED is on, should be off'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


def test_run_script():
    TEST_NAME = 'RUN SCRIPT'
    log.info('{} TEST: test_code.py'.format(TEST_NAME))
    dev.wr_cmd('import test_code', follow=True)
    try:
        assert dev.cmd('test_code.RESULT', silent=True, rtn_resp=True) is True, 'Script did NOT RUN'
        dev.cmd("import sys,gc;del(sys.modules['test_code']);gc.collect()")
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
        assert not dev.cmd('b = 1/0', rtn_resp=True), 'Device Exception: ZeroDivisionError'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


def test_reset():
    TEST_NAME = 'DEVICE RESET'
    log.info('{} TEST'.format(TEST_NAME))
    dev.reset()
    try:
        assert dev.connected, 'Device Not Connected'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


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