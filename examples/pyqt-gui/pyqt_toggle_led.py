import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from upydevice import Device



def main():

    # SerialDevice
    print('Connecting to device...')
    mydev = Device('/dev/tty.SLAB_USBtoUART', init=True)

    # # WebSocketDevice
    # mydev = Device('192.168.1.73', 'keyespw', init=True)

    # # BleDevice
    # mydev = Device('9998175F-9A91-4CA2-B5EA-482AFC3453B9', init=True)
    print('Connected')
    def toggle_led():
        mydev.wr_cmd('led.value(not led.value())')

    app = QApplication(sys.argv)
    widget = QWidget()

    button1 = QPushButton(widget)
    button1.setText("Toggle Led")
    button1.move(100,100)
    button1.clicked.connect(toggle_led)


    widget.setGeometry(50,50,320,200)
    widget.setWindowTitle("Upydevice Button Led Toggle")
    widget.show()
    sys.exit(app.exec_())



if __name__ == '__main__':
   main()
