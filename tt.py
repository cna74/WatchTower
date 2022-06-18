import time
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QCheckBox, QTableWidget,
                             QVBoxLayout, QTableWidgetItem, QLineEdit, QLabel, QDialog,
                             QPushButton, QGridLayout, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal, QThreadPool, QRunnable
from datetime import datetime
from PyQt6 import QtWidgets
import sys
import threading

app = QApplication(sys.argv)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        t = threading.Thread(target=self.job)
        t.start()
        t.join()

    def job(self):
        print(self.__class__.__name__)


window = MainWindow()
window.show()
sys.exit(app.exec())
