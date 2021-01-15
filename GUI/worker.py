import PyQt5.QtCore as qtc
import time
class ThreadClass(qtc.QThread):
    """Runs the progress changes."""

    change_value = qtc.pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        val = 0
        while val < 100:
            val += 1

            time.sleep(.3)
            self.change_value.emit(val)
