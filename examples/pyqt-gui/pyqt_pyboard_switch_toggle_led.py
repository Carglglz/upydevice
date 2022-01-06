import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
import os
from upydevice import Device
import traceback
from PyQt5.QtCore import (QObject, QRunnable, QThreadPool, pyqtSignal,
                          pyqtSlot)
import time
os.environ['QT_MAC_WANTS_LAYER'] = '1'
ICON_RED_LED_OFF = os.path.join(os.getcwd(), "icons/xsled-red-off.png")
ICON_RED_LED_ON = os.path.join(os.getcwd(), "icons/xsled-red-on.png")

# THREAD WORKERS


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        # Return the result of the processing
        finally:
            self.signals.finished.emit()


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
        # Workers
        self.threadpool = QThreadPool()
        self.quit_thread = False
        self._active_listen = True
        # ON EXIT
        self.thread_done = False

        self.start_led_signal()

    def toggle_led(self):
        self._active_listen = False
        self.led.toggle()
        self.dev.wr_cmd("pyb.LED(1).toggle()")
        self._active_listen = True

    def update_led(self, state):
        self.led.toggle()

    def listen_led_state(self, progress_callback):
        while not self.quit_thread:
            if self._active_listen:
                if self.dev.serial.readable() and self.dev.serial.in_waiting:
                    state = self.dev.serial.readline()
                    progress_callback.emit(state)
            time.sleep(0.1)

        print('Thread Done!')
        self.thread_done = True

    def start_led_signal(self):
        # Pass the function to execute
        # Any other args, kwargs are passed to the run function
        worker_led = Worker(self.listen_led_state)
        # worker.signals.result.connect(self.print_output)
        # worker.signals.finished.connect(self.thread_complete)
        # worker.signals.progress.connect(self.progress_fn)
        worker_led.signals.progress.connect(self.update_led)

        # Execute
        self.threadpool.start(worker_led)

    def closeEvent(self, event):
        self.quit_thread = True
        try:
            while not self.thread_done:
                time.sleep(0.5)
                print("shutdown...")
        except Exception as e:
            print(e)
        print("SHUTDOWN COMPLETE")
        sys.exit()


def main():

    # SerialDevice
    pyboard_led_callback = """
def toggle_led():
    pyb.LED(1).toggle()
    if not not pyb.LED(1).intensity():
        print('ON')
    else:
        print('OFF')"""
    print("Connecting to device...")
    mydev = Device("/dev/tty.usbmodem3370377430372", init=True)
    mydev.paste_buff(pyboard_led_callback)
    mydev.wr_cmd('\x04')
    mydev.wr_cmd("sw = pyb.Switch();sw.callback(toggle_led)")
    # # WebSocketDevice
    # mydev = Device('192.168.1.73', 'keyespw', init=True)

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
