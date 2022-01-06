import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
import os
from upydevice import Device

ICON_RED_LED_OFF = os.path.join(os.getcwd(), "icons/xsled-red-off.png")
ICON_RED_LED_ON = os.path.join(os.getcwd(), "icons/xsled-red-on.png")


class LED_Label(QLabel):
    def __init__(self, parent=None):
        super(LED_Label, self).__init__(parent)
        self._value = 0
        self.off = QPixmap(ICON_RED_LED_OFF)  # .scaled(64, 64, Qt.KeepAspectRatio)
        self.on = QPixmap(ICON_RED_LED_ON)  # .scaled(64, 64, Qt.KeepAspectRatio)
        self.setPixmap(self.off)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        if val:
            self.setPixmap(self.on)
            print('on')
        else:
            self.setPixmap(self.off)
            print('off')
        self.repaint()

    def toggle(self):
        self.value = not self._value


class LED_Widget(QWidget):
    def __init__(self, parent=None, dev=None):
        super(LED_Widget, self).__init__(parent)
        self.button = QPushButton(self)
        self.button.setText("Toggle Led")
        self.button.move(100, 100)
        self.dev = dev
        self.led = LED_Label(self)
        self.led.setScaledContents(True)
        self.led.move(140, 50)
        self.button.clicked.connect(self.toggle_led)

    def toggle_led(self):
        self.dev.wr_cmd("led.value(not led.value())")
        self.led.toggle()


def main():

    # SerialDevice
    print("Connecting to device...")
    mydev = Device("/dev/cu.usbserial-016418E3", init=True)

    # # WebSocketDevice
    # mydev = Device('192.168.1.51', 'keyespw', init=True)

    # # BleDevice
    # mydev = Device('9998175F-9A91-4CA2-B5EA-482AFC3453B9', init=True)
    print("Connected")

    app = QApplication(sys.argv)
    led_widget = LED_Widget(dev=mydev)
    led_widget.setGeometry(50, 50, 320, 200)
    led_widget.setWindowTitle("Upydevice Button Led Toggle")
    led_widget.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
