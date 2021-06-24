from upydevice import Device, upy_code
import unittest
import time
from upydevice.phantom import pyb_LED, pyb_Timer, pyb_Servo
import logging
import sys
import pytest
import upydev
import json
import os


_PYBOARD_LITE = '/dev/tty.usbmodem387E386731342'  # PYBOARD LITE
_PYBOARD_ = '/dev/tty.usbmodem3370377430372'  # PYBOARD V1.1
CHECK = '[\033[92m\u2714\x1b[0m]'
XF = '[\u001b[31;1m\u2718\u001b[0m]'

PYBS = [_PYBOARD_LITE, _PYBOARD_]


@pytest.fixture(scope='session', autouse=True)
def dev_name(request):
    return request.config.getoption("--dev")


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
        dev_port = devices[devname][0]
        dev_baud = devices[devname][1]

    else:
        if devname != 'default':
            pass

    if devname == 'default':
        dev = Device(_PYBOARD_, autodetect=True)

    else:
        dev = Device(dev_port, baudrate=dev_baud, autodetect=True)

    extra = {'dev': dev.dev_platform.upper()}
    log = logging.LoggerAdapter(log, extra)


def do_pass(test_name):
    log.info('{} TEST: {}'.format(test_name, CHECK))


def do_fail(test_name):
    log.error('{} TEST: {}'.format(test_name, XF))


# BLINK TEST
_PYBOARD_LED = 1


def test_platform():
    TEST_NAME = 'DEV PLATFORM'
    try:
        log.info('Running SerialDevice test...')
        log.info('DEV PLATFORM: {}'.format(dev.dev_platform))
        print(dev)
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


def test_blink_leds():
    TEST_NAME = 'BLINK LEDS'
    dev.cmd('import pyb')
    for led in range(1, 5):
        for i in range(1):
            dev.cmd('pyb.LED({}).on();LED=True;print("LED: ON")'.format(led))
            dev.cmd('pyb.LED({}).off();LED=False;print("LED: OFF")'.format(led))
    try:
        assert dev.cmd('not LED', rtn_resp=True,
                       silent=True), 'LED is on, should be off'
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


# SWITCH TEST
def test_user_sw():
    TEST_NAME = 'USER SWITCH'
    dev.cmd('sw = pyb.Switch()')
    log.info('{} TEST: please press and hold the switch now'.format(TEST_NAME))
    t = 0
    while not dev.cmd('sw.value()', rtn_resp=True, silent=True):
        time.sleep(0.5)
        t += 1
        if t % 2 == 0:
            print('Time out in {} s\r'.format(int((20 - t)/2)), end='')
        if t > 20:
            log.info('{} TEST: Time out after 10s'.format(TEST_NAME))
            break

    try:
        assert dev.cmd('sw.value()', rtn_resp=True, silent=True)
        do_pass(TEST_NAME)
        log.info('{} TEST: you can release the switch now.'.format(TEST_NAME))
        while dev.cmd('sw.value()', rtn_resp=True, silent=True):
            pass
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


# PHANTOM TEST

def test_phantom_led():
    TEST_NAME = 'PHANTOM LED'
    led = pyb_LED(dev, _PYBOARD_LED)
    led.toggle()
    led_value = True
    led.toggle()
    led_value = False

    try:
        assert not led_value
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


def test_phantom_timer():
    # Define callback
    TEST_NAME = 'TIMER'
    pyb = ''
    log.info('{} TEST at 2 Hz: LED CALLBACK:'.format(TEST_NAME))

    @upy_code
    def led_toggle(x):
        for led in range(1, 5):
            pyb.LED(led).toggle()
            pyb.delay(50)

    def_callback_str = led_toggle() + '\r' * 6
    dev.cmd(def_callback_str, silent=True)

    def led_toggle():
        pass

    # Define timer
    dev.cmd('from pyb import Timer;Tim = Timer(4)')
    pbt = pyb_Timer(dev, 'Tim')

    # Init Timer
    pbt.init(freq=2, callback=led_toggle)
    led_value = True
    time.sleep(2)
    pbt.deinit()
    for led in range(1, 5):
        led_value = dev.cmd('pyb.LED({}).off(); False'.format(led),
                                silent=True, rtn_resp=True)
    try:
        assert not led_value
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


# SERVO TEST
def test_servo():
    TEST_NAME = 'SERVO X2'
    pybservo = pyb_Servo(dev, name='s2', number=2, init=True)
    pybservo.angle(90)
    time.sleep(1)
    pybservo.angle(-60, 3000)
    time.sleep(3.5)
    s2_att = dev.cmd("dir(s2)", silent=True, rtn_resp=True)
    try:
        assert isinstance(s2_att, list), 'Expected a list, receviced : {}'.format(type(s2_att))
        do_pass(TEST_NAME)
        print('Test Result: ', end='')
    except Exception as e:
        do_fail(TEST_NAME)
        print('Test Result: ', end='')
        raise e


# OS TEST

# Listdir
def test_os_list_dir():
    TEST_NAME = 'OS LIST DIR'
    log.info('{} TEST: {}'.format(TEST_NAME, "import os;os.listdir()"))
    ls = dev.cmd('import os;os.listdir()', rtn_resp=True)
    try:
        assert isinstance(ls, list), 'Expected a list, receviced : {}'.format(type(ls))
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
        assert dev.cmd('test_code.RESULT', silent=False, rtn_resp=True) is True, 'Script did NOT RUN'
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


if __name__ == '__main__':
    unittest.main()
