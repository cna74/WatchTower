from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QCheckBox, QTableWidget,
                             QVBoxLayout, QTableWidgetItem, QLineEdit, QLabel, QDialog,
                             QPushButton, QGridLayout, QComboBox)
from PyQt6 import QtWidgets
import sys
import api
import db


app = QApplication(sys.argv)


class AddProduct(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(400, 300)
        self.create_dialog()
        self.show()

    def create_dialog(self):
        layout = QGridLayout()
        self.live_check = QCheckBox("live check")
        self.live_check.toggled.connect(self.check_dkp)
        self.DKP = QLineEdit()
        self.DKP.setPlaceholderText("DKP")
        self.DKP.textChanged.connect(self.check_dkp)

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("product name")

        self.your_price = QLineEdit()
        self.your_price.textChanged.connect(self.comma_separate)
        self.your_price.setPlaceholderText("your price")

        self.price_on_digi = QLineEdit()
        self.price_on_digi.setPlaceholderText("digikala price")

        self.DKPC = QLineEdit()
        self.DKPC.setPlaceholderText("DKPC")

        self.seller = QComboBox()
        self.seller.setPlaceholderText("seller")
        self.color = QComboBox()
        self.color.setPlaceholderText("color")

        cancel, ok = QPushButton("Cancel"), QPushButton("OK")
        cancel.clicked.connect(self.cancel_button)
        ok.clicked.connect(self.ok_button)

        layout.addWidget(self.DKP, 0, 0)
        layout.addWidget(self.live_check, 0, 1)
        layout.addWidget(self.product_name, 1, 0)
        layout.addWidget(self.your_price, 2, 0)
        layout.addWidget(self.price_on_digi, 3, 0)
        layout.addWidget(self.DKPC, 4, 0)
        layout.addWidget(self.seller, 1, 1)
        layout.addWidget(self.color, 2, 1)

        layout.addWidget(cancel, 5, 0)
        layout.addWidget(ok, 5, 1)
        self.setLayout(layout)

    def check_dkp(self):
        dkp = self.DKP.text()
        if self.live_check.isChecked():
            if str(dkp).isdigit():
                # get product data
                status, variants, name = api.get_data(dkp)
                # set product name
                self.product_name.setText(name)
                # add sellers to ComboBox
                [self.seller.addItem(v.seller_name) for v in variants]
                self.seller.setCurrentIndex(0)
                # add colors to ComboBox
                [self.color.addItem(v.color) for v in variants]
                self.color.setCurrentIndex(0)

                # set price of selected seller
                price_on_digi = [v.price if v.seller_name == self.seller.currentText() else "" for v in variants]
                self.price_on_digi.setText(f"{int(price_on_digi[0]):,}")

            else:
                name = ""
            # self.product_name.setText(name)

    def cancel_button(self):
        self.close()

    def ok_button(self):
        db.add(db.Product(DKP=int(self.DKP.text()), name=self.product_name.text()))
        self.close()

    def comma_separate(self, price):
        price = "".join(str(price).split(","))
        if str(price).isdigit():
            self.your_price.setText(f"{int(price):,}")


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
