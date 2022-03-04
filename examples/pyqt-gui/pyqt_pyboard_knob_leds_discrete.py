import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QHBoxLayout, QDial
from PyQt5.QtCore import Qt
from upydevice import Device
import os

os.environ['QT_MAC_WANTS_LAYER'] = '1'


class KnobsLedpanel(QWidget):
    def __init__(self, parent=None, device=None):
        super(KnobsLedpanel, self).__init__(parent)

        layout = QHBoxLayout()
        self.knob_yellow_led = QDial()
        self.knob_blue_led = QDial()

        self.knob_yellow_led.setMinimum(0)
        self.knob_yellow_led.setMaximum(255)
        self.knob_yellow_led.setValue(0)
        self.knob_yellow_led.sliderReleased.connect(self.yellow_sliderMoved)

        self.knob_blue_led.setMinimum(0)
        self.knob_blue_led.setMaximum(255)
        self.knob_blue_led.setValue(0)
        self.knob_blue_led.sliderReleased.connect(self.blue_sliderMoved)

        layout.addSpacing(15)
        layout.addWidget(self.knob_yellow_led)
        layout.addWidget(self.knob_blue_led)
        self.setLayout(layout)
        # self.setGeometry(10, 10, 350, 250)

        self.device = device

    def yellow_sliderMoved(self):
        self.device.wr_cmd(f"yled.intensity({self.knob_yellow_led.value()})")
        print(f"Yellow Led intensity: {self.knob_yellow_led.value()}")

    def blue_sliderMoved(self):
        self.device.wr_cmd(f"bled.intensity({self.knob_blue_led.value()})")
        print(f"Blue Led intensity: {self.knob_blue_led.value()}")


def main():

    # SerialDevice
    print("Connecting to device...")
    mydev = Device("/dev/tty.usbmodem3370377430372", init=True)
    mydev.wr_cmd("from pyb import LED;yled = LED(3); bled= LED(4)")
    # # WebSocketDevice
    # mydev = Device('192.168.1.73', 'keyespw', init=True)

    # # BleDevice
    # mydev = Device('9998175F-9A91-4CA2-B5EA-482AFC3453B9', init=True)
    print("Connected")

    app = QApplication(sys.argv)

    KnobLedController = KnobsLedpanel(device=mydev)

    KnobLedController.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
