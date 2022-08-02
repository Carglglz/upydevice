from upydevice import Device

bled = Device('9998175F-9A91-4CA2-B5EA-482AFC3453B9', init=True)

@bled.code
def beep():
    bz.beep_interrupt()
