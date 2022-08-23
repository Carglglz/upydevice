from upydevice import Device

pyb = Device('/dev/tty.usbmodem3370377430372')
# espd = Device('espdev.local', "oXQdh0wQ:espkeyhack", init=True)
# bled = Device('00FEFE2D-5983-4D6C-9679-01F732CBA9D9', init=True)


@pyb.code
def led_toggle(led):
    pyb.LED(led).toggle()


# @bled.code
# def led_esp_toggle():
#     led.value(not led.value())


print('Toggling led..')
for i in range(1, 5):
    led_toggle(i)


@pyb.code_follow
def dothis():
    import time
    for i in range(5):
        print("hello")
        time.sleep(0.5)


dothis()

# espd = Device('espdev.local', "oXQdh0wQ", init=True)

# @espd.code
# def esp_led_toggle():
#     led.value(not led.value())
#     return 1
#
#
#
# print('Toggling esp led..')
#
# res1=esp_led_toggle()
# led_esp_toggle()
#
# @bled.code_follow
# def dothat():
#     for i in range(5):
#         print("hello")
#         time.sleep(0.5)
#
#
# dothat()
#
#
# @espd.code_follow
# def doit():
#     for i in range(5):
#         print("hello")
#         time.sleep(0.5)
#
#
# doit()
# res2 = espd.wr_cmd('esp_led_toggle()', rtn=True, rtn_resp=True)
# print(res1 + 1)
