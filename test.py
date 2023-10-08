import logging
import os
import random
import sys
import time
from time import sleep
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#live sync nw ui and py files
from PyQt5.uic import loadUiType
from pytube import YouTube
from pytube import Playlist


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)


    def run(self):
        for i in range (5):
            sleep(1)
            self.progress.emit(i + 1)
        self.finished.emit()


logging.basicConfig(format="%(message)s", level=logging.INFO)

class Runni(QRunnable):
    def __init__(self, n):
        super().__init__()
        self.n = n

    def run(self):
        for i in range(5):
            logging.info(f"working in thread number {self.n}, step {i+ 1}/5")
            time.sleep(random.randint(700, 2500) / 1000)



form_class, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'testpage.ui'))

class Window(QMainWindow, form_class):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        QMainWindow.__init__(self)
        self.cnt = 0
        self.setupUi(self)
        self.handle_ui()
        self.handle_buttons()


    def handle_ui(self):
        self.setWindowTitle("Test Threading")


    def handle_buttons(self):
        self.pushButton.clicked.connect(self.contClicks)
        self.pushButton_2.clicked.connect(self.longTask)

    def contClicks(self):
        self.cnt += 1
        self.label.setText(f"Counting: {self.cnt} clicks !")


    def reportProgress(self, n):
        self.label_2.setText(f"Long-Running step: {n}")


    def longTask(self):
        # # 2 - Qthread object
        # self.thread = QThread()

        # # 3 - worker object
        # self.worker = Worker()

        # # 4 - MOVE WORKER TO THREAD
        # self.worker.moveToThread(self.thread)

        # # 5 - connect signals
        # self.thread.started.connect(self.worker.run)
        # self.worker.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.progress.connect(self.reportProgress)

        # # 6 - start thread

        # self.thread.start()
        # self.pushButton_2.setEnabled(False)
        # self.thread.finished.connect(lambda: self.pushButton_2.setEnabled(True))
        # self.thread.finished.connect(lambda:self.label_2.setText("Long-running step: 0"))


        # REUSABLE THREADS : QRunnable & QThreadPool

        #will depend on your specific hardware and is normally based on the cores of your CPU
        threadsNumber = QThreadPool.globalInstance().maxThreadCount()

        self.label_2.setText(f"Running {threadsNumber} Threads")
        pool = QThreadPool.globalInstance()

        for i in range(threadsNumber):
            # 2 - instanitate subclass of QRunnable
            runnabel = Runni(i)
            # 3 - call start()
            pool.start(runnabel)







def main():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()