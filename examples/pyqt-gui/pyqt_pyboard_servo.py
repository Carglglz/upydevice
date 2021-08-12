import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QSlider, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from upydevice import Device


class Slider(QWidget):
    def __init__(self, parent=None, device=None):
        super(Slider, self).__init__(parent)

        layout = QHBoxLayout()
        self.l1 = QLabel("Angle")
        self.l1.setAlignment(Qt.AlignCenter)
        self.label = QLabel('0', self)
        self.label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.label.setMinimumWidth(80)

        self.sl = QSlider(Qt.Horizontal, self)
        self.sl.setRange(-30, 90)
        self.sl.setPageStep(5)
        self.sl.setValue(10)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(10)
        self.sl.valueChanged.connect(self.updateLabel)
        self.sl.sliderReleased.connect(self.valuechange)

        layout.addWidget(self.sl)
        layout.addSpacing(15)
        layout.addWidget(self.l1)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setGeometry(10, 10, 350, 250)

        self.device = device

    def valuechange(self):
        angle = self.sl.value()
        self.device.wr_cmd('s1.angle({}, 1000)'.format(
                angle))
        print(f'Setting angle to {angle}')

    def updateLabel(self, value):

        self.label.setText(str(value))



def main():

    # SerialDevice
    print('Connecting to device...')
    mydev = Device('/dev/tty.usbmodem3370377430372', init=True)
    mydev.wr_cmd('from pyb import Servo;s1 = Servo(1)')
    # # WebSocketDevice
    # mydev = Device('192.168.1.73', 'keyespw', init=True)

    # # BleDevice
    # mydev = Device('9998175F-9A91-4CA2-B5EA-482AFC3453B9', init=True)
    print('Connected')

    app = QApplication(sys.argv)
    widget = QWidget()

    angle_slider = Slider(parent=widget, device=mydev)
    # angle_slider.show()



    # widget.setGeometry(300,300,350,250)
    widget.setWindowTitle("Pyboard Servo slider")
    widget.show()
    sys.exit(app.exec_())



if __name__ == '__main__':
   main()
