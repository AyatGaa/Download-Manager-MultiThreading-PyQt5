import os.path
import sys
import logging
import time
from time import sleep

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType

page, _ = loadUiType(os.path.join(os.path.dirname(__file__), "last.ui"))


class mainWindow(QMainWindow, page):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        icon = QIcon()
        icon.addPixmap(QPixmap("R.png"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.handel_Buttons()
        self.verticalSlider.valueChanged.connect(self.lcdNumber.display)

    def handel_Buttons(self):
        self.pushButton.clicked.connect(self.start_btn_clicked)
        self.pushButton_2.clicked.connect(self.STOP_btn_clicked)

    def start_btn_clicked(self):
        self.worker = threadClass()
        self.worker.start()
        # self.worker.finished.connect(self.worker_finish)
        self.worker.update_progress.connect(self.fn_update_progress)
        self.worker.work_complete.connect(self.worker_finish)

    def STOP_btn_clicked(self):
        self.worker.isRunning = False
        self.pushButton.setEnabled(True)
        self.worker.terminate()

    def fn_update_progress(self, val):
        self.progressBar.setValue(val)
        self.pushButton.setEnabled(False)

    def worker_finish(self, data):
        QMessageBox.information(self, "done", " thread Class Done! \n\n{} {} {}".format(data['name'], data['ln'], data['id']))


# worker clas
class threadClass(QThread):
    #  dont need to override parent class so will not define constructor
    #  if I dont create signal there are defult signal ( finish and start )
    #  they called from Qthread counstructor
    #  BUT, IF  I NEED TO UPDATE WITH DATA so i need to create signal !
    update_progress = pyqtSignal(int)  # pass type of passed info to it
    work_complete = pyqtSignal(dict)

    def run(self):
        for x in range(20, 110, 10):
            print(x)
            time.sleep(0.5)
            self.update_progress.emit(x)
        self.work_complete.emit({"id": 12, "name": "ayat", "ln": "Gamal "})

def main():
    app = QApplication(sys.argv)
    win = mainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
