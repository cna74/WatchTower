from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QTableWidget, QStatusBar, QVBoxLayout,
                             QTableWidgetItem, QLabel)
from ui import setting, editProduct, addProduct
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
from PyQt6 import QtGui
import threading
import datetime
import time
import util
import sys
import db

app = QApplication(sys.argv)


class Monitor(QWidget):
    def __init__(self):
        super().__init__()
        self.headers = db.Product.__table__.columns.keys()

        self.table = QTableWidget()
        self.table.setRowCount(1)
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.cellClicked.connect(self.selected_cell)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # self.table.setDisabled(True)
        self.current_row = None
        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.table)
        self.setLayout(self.vBox)
        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_R:
            self.fill_table_from_db()
        elif event.key() == Qt.Key.Key_Delete:
            if isinstance(self.current_row, int):
                db.remove(int(self.table.item(self.current_row, 0).text()))
                self.table.removeRow(self.current_row)
        else:
            pass

    def selected_cell(self, row, _):
        if isinstance(row, int):
            self.current_row = row

    def fill_table_from_db(self):
        data = db.get_products()
        if len(data) > self.table.rowCount():
            self.table.setRowCount(len(data))
        for i, product in enumerate(data, start=0):
            for c, column in enumerate(self.headers):
                if column in ("bybox", "low", "high", "my_sell_price"):
                    self.table.setItem(i, c, QTableWidgetItem(str(util.add_comma(product.__dict__[column]))))
                else:
                    self.table.setItem(i, c, QTableWidgetItem(str(product.__dict__[column])))

        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.refresh_rate = util.configure()
        self.resize(1400, 500)
        self.setWindowTitle("Digi Watchtower")
        self.monitor = Monitor()
        self.monitor.table.cellDoubleClicked.connect(self.edit_product)
        self.setCentralWidget(self.monitor)
        # menubar
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        add = self.fileMenu.addAction("Add product")
        add.triggered.connect(self.add_product)
        refresh = self.menuBar.addAction("Refresh")
        setting = self.menuBar.addAction("Setting")
        setting.triggered.connect(self.set_setting)
        refresh.triggered.connect(self.update_database)
        # status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.ETA = QLabel()
        self.last_update = QLabel()
        self.message = QLabel()
        self.statusBar.addWidget(self.last_update)
        self.statusBar.addWidget(QLabel("|"))
        self.statusBar.addWidget(self.ETA)
        self.statusBar.addWidget(QLabel("|"))
        self.statusBar.addWidget(self.message)
        self.statusBar.show()
        self.monitor.fill_table_from_db()
        # thread
        self.stop_thread = False
        self.thread = threading.Thread(target=self.update_timer, args=(lambda: self.stop_thread,))
        self.thread.start()
        self.update_database(startup=True)

        self.show()

    def update_database(self, startup=False):
        if startup:
            db.update_all()
            self.monitor.fill_table_from_db()
            self.last_update.setText(datetime.datetime.now().strftime("%X"))
        else:
            db.update_all()
            self.monitor.fill_table_from_db()
            self.last_update.setText(datetime.datetime.now().strftime("%X"))
            self.stop_thread = True
            self.thread.join()
            self.thread = threading.Thread(target=self.update_timer, args=(lambda: self.stop_thread,))
            self.stop_thread = False
            self.thread.start()

    def update_timer(self, stop_thread):
        delta = datetime.timedelta(minutes=self.refresh_rate)
        seconds = delta.seconds
        while True:
            for s in range(seconds, 0, -1):
                self.ETA.setText(str(datetime.timedelta(seconds=s)))
                if s == 0:
                    db.update_all()
                    self.update_database()
                    self.monitor.fill_table_from_db()
                if stop_thread():
                    break
                time.sleep(1)
            if stop_thread():
                break

    def add_product(self):
        dialog = addProduct.AddProduct()
        dialog.exec()
        self.monitor.fill_table_from_db()

    def set_setting(self):
        s = setting.Setting()
        s.exec()
        current_regresh_rate = self.refresh_rate
        self.refresh_rate = s.refresh_rate
        if not current_regresh_rate == self.refresh_rate:
            self.stop_thread = True
            self.thread.join()
            self.stop_thread = False
            self.thread = threading.Thread(target=self.update_timer, args=(lambda: self.stop_thread,))
            self.thread.start()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.stop_thread = True
        self.thread.join()
        event.accept()

    def edit_product(self):
        edit_p = editProduct.EditProduct()
        edit_p.exec()


window = MainWindow()
window.show()
sys.exit(app.exec())
