from upydevice import Device

# pyb = Device('/dev/tty.usbmodem3370377430372')
espd = Device('espdev.local', "oXQdh0wQ", init=True)
bled = Device('00FEFE2D-5983-4D6C-9679-01F732CBA9D9', init=True)
#@pyb.code
#def led_toggle(led):
#    pyb.LED(led).toggle()
@bled.code
def led_toggle():
    led.value(not led.value())




print('Toggling led..')
#for i in range(1,5):
led_toggle()


# espd = Device('espdev.local', "oXQdh0wQ", init=True)

@espd.code
def esp_led_toggle():
    led.value(not led.value())
    return 1



print('Toggling esp led..')

res1 = esp_led_toggle()
# res2 = espd.wr_cmd('esp_led_toggle()', rtn=True, rtn_resp=True)
print(res1 + 1)
