import os.path
import sys
import logging
from time import sleep

from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
logging.basicConfig(format="%(message)s", level=logging.INFO)

form_class,_ = loadUiType(os.path.join(os.path.dirname(__file__), "threadtest.ui"))

class Threads(QMainWindow, form_class):
    def __init__(self, parent=None):
        super(Threads, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_ui()
        self.handle_buttons()
        icon = QIcon()
        icon.addPixmap(QPixmap("R.png"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.thread = {}

    def handle_ui(self):
        self.setWindowTitle("More than one thread !")

    def handle_buttons(self):
        self.pushButton.clicked.connect(self.start_1)
        self.pushButton_2.clicked.connect(self.start_2)
        self.pushButton_3.clicked.connect(self.start_3)
        self.pushButton_4.clicked.connect(self.stop_1)
        self.pushButton_5.clicked.connect(self.stop_2)
        self.pushButton_6.clicked.connect(self.stop_3)

    def start_1(self):
        self.thread[1] = ThreadClass(parent=None, index=1)
        self.thread[1].start()
        self.thread[1].any_signal.connect(self.threadFunction)
        self.pushButton.setEnabled(False)


    def start_2(self):
        self.thread[2] = ThreadClass(parent=None, index=2)
        self.thread[2].start()
        self.thread[2].any_signal.connect(self.threadFunction)
        self.pushButton_2.setEnabled(False)

    def start_3(self):
        self.thread[3] = ThreadClass(parent=None, index=3)
        self.thread[3].start()
        self.thread[3].any_signal.connect(self.threadFunction)
        self.pushButton_3.setEnabled(False)

    def stop_1(self):
        self.thread[1].stop()
        self.pushButton.setEnabled(True)

    def stop_2(self):
        self.thread[2].stop()
        self.pushButton_2.setEnabled(True)

    def stop_3(self):
        self.thread[3].stop()
        self.pushButton_3.setEnabled(True)


    def threadFunction(self,counter):
        cnt = counter
        index = self.sender().index
        if index == 1:
            self.progressBar.setValue(cnt)
        if index == 2:
            self.progressBar_2.setValue(cnt)
        if index == 3:
            self.progressBar_3.setValue(cnt)


class ThreadClass(QThread):
    any_signal = pyqtSignal(int)
    def __init__(self, parent= None , index = 0):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        # self.isRunning == True

    def run(self):
        logging.info(f"thead number {self.index} start")
        cnt = 0
        while True:
            cnt += 1
            if cnt == 99 : cnt = 0
            sleep(0.1)
            self.any_signal.emit(cnt)
    def stop(self):
        self.isRunning = False
        logging.info(f"thead number {self.index} STOP")
        self.terminate()

def main():

    app = QApplication(sys.argv)
    win = Threads()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()