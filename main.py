from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QCheckBox, QTableWidget,
                             QVBoxLayout, QTableWidgetItem, QLineEdit, QLabel, QDialog,
                             QPushButton, QGridLayout)
from PyQt6 import QtWidgets
import sys
import api
import db


app = QApplication(sys.argv)


class AddProduct(QDialog):
    def __init__(self):
        super().__init__()
        self.create_dialog()
        self.show()

    def create_dialog(self):
        layout = QGridLayout()
        label = QLabel("Ender DKP:")
        self.live_check = QCheckBox("live check")
        self.live_check.toggled.connect(self.check_dkp)
        self.text_box = QLineEdit()
        self.text_box.textChanged.connect(self.check_dkp)
        self.result = QLabel()
        cancel, ok = QPushButton("Cancel"), QPushButton("OK")
        cancel.clicked.connect(self.cancel_button)
        ok.clicked.connect(self.ok_button)
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.text_box, 1, 0)
        layout.addWidget(self.live_check, 1, 1)
        layout.addWidget(self.result, 2, 0)
        layout.addWidget(cancel, 3, 0)
        layout.addWidget(ok, 3, 1)
        self.setLayout(layout)

    def check_dkp(self):
        dkp = self.text_box.text()
        if self.live_check.isChecked():
            if str(dkp).isdigit():
                name = api.get_data(dkp)
            else:
                name = ""
            self.result.setText(name)

    def cancel_button(self):
        self.close()

    def ok_button(self):
        db.add(db.Product(DKP=int(self.text_box.text()), name=self.result.text()))
        self.close()


class Monitor(QWidget):
    def __init__(self):
        super().__init__()
        self.CreateTable()
        self.show()

    def CreateTable(self):
        self.table = QTableWidget()
        self.table.setRowCount(10)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["DKP", "name", "my sell price", "digi sell price"])

        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.table)
        self.setLayout(self.vBox)

    def refresh(self):
        data = db.get_products()
        for i, j in enumerate(data, start=0):
            self.table.setItem(i, 0, QTableWidgetItem(str(j.DKP)))
            self.table.setItem(i, 1, QTableWidgetItem(str(j.name)))
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(720, 500)
        self.setWindowTitle("Digi Watchtower")
        self.monitor = Monitor()
        self.setCentralWidget(self.monitor)
        self.monitor.refresh()

        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        add = self.fileMenu.addAction("add product")
        add.triggered.connect(self.add_product)
        refresh = self.menuBar.addAction("refresh")
        refresh.triggered.connect(self.monitor.refresh)
        self.show()

    def add_product(self):
        dialog = AddProduct()
        dialog.exec()
        self.monitor.refresh()


# monitor = Monitor()
window = MainWindow()

window.show()

sys.exit(app.exec())
