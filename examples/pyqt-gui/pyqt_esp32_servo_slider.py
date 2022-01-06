import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QSlider, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from upydevice import Device
import os

os.environ['QT_MAC_WANTS_LAYER'] = '1'

_SERVO_PIN = 14


class Slider(QWidget):
    def __init__(self, parent=None, device=None):
        super(Slider, self).__init__(parent)

        layout = QHBoxLayout()
        self.l1 = QLabel("Angle")
        self.l1.setAlignment(Qt.AlignCenter)
        self.label = QLabel("0", self)
        self.label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.label.setMinimumWidth(80)

        self.sl = QSlider(Qt.Horizontal, self)
        self.sl.setRange(-30, 90)
        self.sl.setPageStep(5)
        self.sl.setValue(10)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(10)
        self.sl.valueChanged.connect(self.move_servo)
        # self.sl.sliderReleased.connect(self.valuechange)

        layout.addWidget(self.sl)
        layout.addSpacing(15)
        layout.addWidget(self.l1)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setGeometry(10, 10, 350, 250)

        self.device = device

    def move_servo(self, value):
        # self.device.cmd_nb(f"s1.angle({value}, 1000)", block_dev=False)
        self.device.cmd_nb(f"s1.write_angle({value})", block_dev=False)
        print(f"Setting angle to {value}")
        self.label.setText(f"{value}")


def main():

    # SerialDevice
    print("Connecting to device...")
    # mydev = Device("/dev/tty.usbmodem3370377430372", init=True)
    # # WebSocketDevice
    # mydev = Device('192.168.1.73', 'keyespw', init=True)

    # # BleDevice

    mydev = Device('9998175F-9A91-4CA2-B5EA-482AFC3453B9', init=True)
    mydev.wr_cmd(f"from servo import Servo;s1 = Servo(Pin({_SERVO_PIN}))")
    print("Connected")

    app = QApplication(sys.argv)
    widget = QWidget()

    angle_slider = Slider(parent=widget, device=mydev)
    # angle_slider.show()

    # widget.setGeometry(300,300,350,250)
    widget.setWindowTitle("Pyboard Servo slider")
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
