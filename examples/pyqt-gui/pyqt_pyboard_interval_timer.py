import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
                             QMainWindow)
from PyQt5.QtGui import QPixmap
import os
from upydevice import Device
import traceback
from PyQt5.QtCore import (QObject, QRunnable, QThreadPool, pyqtSignal,
                          pyqtSlot, Qt, QMargins, QTimer)
from PyQt5.QtMultimedia import QSound
import time
from datetime import timedelta
import os

os.environ['QT_MAC_WANTS_LAYER'] = '1'
# ICON_RED_LED_OFF = os.path.join(os.getcwd(), "icons/xsled-red-off.png")
# ICON_RED_LED_ON = os.path.join(os.getcwd(), "icons/xsled-red-on.png")
TIMER_FX = os.path.join(os.getcwd(), "sounds/beep-07a.wav")
TIMER_FX3 = os.path.join(os.getcwd(), "sounds/beep-3.wav")

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


class MainWindow(QMainWindow):
    def __init__(self, widgetlist):
        super().__init__()
        # self.setStyleSheet("background-color: black;")
        self.widgets = widgetlist
        self.setWindowTitle("Test App")
        self.setGeometry(50, 50, 400, 600)
        layout = QVBoxLayout()
        for w in widgetlist:
            layout.addWidget(w)

        widget = QWidget()
        widget.setLayout(layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

    # Keypressevents

    def closeEvent(self, event):
        self.widgets[0].closeEvent(event)


class ActionLabel(QLabel):
    def __init__(self, parent=None):
        super(ActionLabel, self).__init__(parent)
        self._value = 0
        self.rest_bg = "background-color: rgb(0,255,0); color: white;"
        self.work_bg = "background-color: red; color: white;"
        self.finished_bg = "background-color: blue; color: white;"
        self._type_action_style = {'P': self.rest_bg,
                                   'R': self.rest_bg, 'W': self.work_bg}
        self._type_action = {'P': "PREPARE", 'R': "REST", 'W': "WORK"}
        self.setStyleSheet(self.rest_bg)
        font = self.font()
        font.setPointSize(60)
        self.setFont(font)
        self.setText("PREPARE")
        self.resize(400, 100)
        self.setAlignment(Qt.AlignCenter)
        # self.setMargin(10)
        # self.setScaledContents(True)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        if val:
            # self.setStyleSheet(self.work_bg)
            # self.setText("WORK")
            print('on')
        else:
            # self.setStyleSheet(self.rest_bg)
            # self.setText("REST")
            print('off')
        self.repaint()

    def toggle(self):
        self.value = not self._value


class TimerLabel(QLabel):
    def __init__(self, parent=None):
        super(TimerLabel, self).__init__(parent)
        self._value = 0
        self._intervals = [('P', 5), ('W', 5), ('R', 5), ('W', 5), ('R', 5)]
        self._int_gen = (interval for interval in self._intervals)
        self.color = "color: white;"
        self.setStyleSheet(self.color)
        font = self.font()
        font.setPointSize(120)
        self.setFont(font)
        self.setText("00:00")
        self.resize(400, 200)
        self.setAlignment(Qt.AlignCenter)
        # self.setMargin(10)
        # self.setScaledContents(True)

    def reset_intervals(self):
        self._int_gen = (interval for interval in self._intervals)


class ActionWidget(QWidget):
    def __init__(self, parent=None, dev=None):
        super(ActionWidget, self).__init__(parent)
        self.setStyleSheet("background-color: black;")
        vbox = QVBoxLayout()
        self.dev = dev
        self.action = ActionLabel(self)
        self.timerlabel = TimerLabel(self)
        vbox.addWidget(self.action)
        vbox.addWidget(self.timerlabel)
        vbox.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setLayout(vbox)
        # Workers
        self.threadpool = QThreadPool()
        self.quit_thread = False
        self._active_listen = True
        # Timer
        self._interval_done = True
        self._interval_time = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self.iterate)
        # Sound
        self.timer_sound = QSound(TIMER_FX)
        self.interval_sound = QSound(TIMER_FX3)
        # Button
        self._button = None
        # ON EXIT
        self.thread_done = False

        self.start_action_signal()

    def toggle_led(self):
        self._active_listen = False
        self.dev.wr_cmd("pyb.LED(1).toggle()")
        self.action.toggle()
        self._active_listen = True
        if self.action.value:
            self._timer.start(1000)
        else:
            self._timer.stop()

    def update_state(self, state):
        self.action.toggle()
        self._button.pushbutton(True)
        if state == "ON":
            self._timer.start(1000)
        else:
            self._timer.stop()

    def listen_action_state(self, progress_callback):
        while not self.quit_thread:
            if self._active_listen:
                if self.dev.serial.readable() and self.dev.serial.in_waiting:
                    state = self.dev.serial.readline().decode().replace('\r\n', '')
                    progress_callback.emit(state)
                    print(state)
            time.sleep(0.1)

        print('Thread Done!')
        self.thread_done = True

    def start_action_signal(self):
        # Pass the function to execute
        # Any other args, kwargs are passed to the run function
        worker_led = Worker(self.listen_action_state)
        # worker.signals.result.connect(self.print_output)
        # worker.signals.finished.connect(self.thread_complete)
        # worker.signals.progress.connect(self.progress_fn)
        worker_led.signals.progress.connect(self.update_state)

        # Execute
        self.threadpool.start(worker_led)

    def iterate(self):
        try:
            if self._interval_done:
                interval_type, self._interval_time = next(self.timerlabel._int_gen)
                self.action.setStyleSheet(self.action._type_action_style[interval_type])
                self.action.setText(self.action._type_action[interval_type])
                self.timerlabel.setText(
                    str(timedelta(seconds=self._interval_time)).split('.')[0][2:])
                self._interval_done = False
            else:
                self._interval_time -= 1
                if self._interval_time > 0 and self._interval_time <= 3:
                    self.timer_sound.play()
                elif self._interval_time == 0:
                    self._interval_done = True
                    self.interval_sound.play()
                self.timerlabel.setText(
                    str(timedelta(seconds=self._interval_time)).split('.')[0][2:])

        except StopIteration:
            self.toggle_led()
            self.finish_state()
            self.timerlabel.reset_intervals()
            self._button.pushbutton(True)

    def finish_state(self):
        self.action.setStyleSheet(self.action.finished_bg)
        self.action.setText("Finished")
        self.timerlabel.setText("00:00")

    def closeEvent(self, event):
        self._timer.stop()
        self.quit_thread = True
        try:
            while not self.thread_done:
                time.sleep(0.5)
                print("shutdown...")
        except Exception as e:
            print(e)
        print("SHUTDOWN COMPLETE")
        sys.exit()


class ControlsWidget(QWidget):
    def __init__(self, parent=None, dev=None, action_label=None):
        super(ControlsWidget, self).__init__(parent)
        vbox = QVBoxLayout()
        self.button = QPushButton(self)
        self.button.setText("Start")
        self._value = False
        # self.button.setStyleSheet("background-color: white;")
        # self.button.move(100, 100)
        self.dev = dev
        # self.action.setScaledContents(True)
        # self.action.move(140, 50)
        self.action = action_label
        self.button.clicked.connect(self.pushbutton)
        vbox.addWidget(self.button)
        vbox.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setLayout(vbox)

    def pushbutton(self, soft=False):
        if not self._value:
            self.button.setText("Stop")
        else:
            self.button.setText("Start")

        self._value = not self._value
        if not soft:
            self.action.toggle_led()
        self.action.timer_sound.play()


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
    action_widget = ActionWidget(dev=mydev)
    # action_widget.setGeometry(50, 50, 400, 600)
    # action_widget.setWindowTitle("Upydevice Button Led Toggle")
    controls_widget = ControlsWidget(dev=mydev, action_label=action_widget)
    action_widget._button = controls_widget
    main_w = MainWindow([action_widget, controls_widget])
    # action_widget.show()
    main_w.show()

    app.exec_()


if __name__ == "__main__":
    main()
