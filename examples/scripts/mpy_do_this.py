from upydevice import Device

# Script to toggle on board led, "led" must be defined in the device for this to work.

def main():
    # SerialDevice
    mydev = Device('/dev/tty.usbmodem3370377430372', init=True)

    # WebSocketDevice
    # mydev = Device('192.168.1.73', 'keyespw', init=True)

    # # BleDevice
    # mydev = Device('9998175F-9A91-4CA2-B5EA-482AFC3453B9', init=True)

#    mydev.wr_cmd('led.value(not led.value())')
    mydev.wr_cmd('led.toggle()')
    mydev.disconnect()


if __name__ == '__main__':
    main()
