import pandas
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QCheckBox, QTableWidget,
                             QVBoxLayout, QTableWidgetItem, QLineEdit, QLabel, QDialog,
                             QPushButton, QGridLayout, QComboBox)
from PyQt6 import QtWidgets
import sys
import api
import db
import util

app = QApplication(sys.argv)


class AddProduct(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(500, 400)
        self.lowest = self.highest = self.bybox = self.variants = None
        layout = QGridLayout()
        dkp, name, price, digi_price, dkpc, self.count, self.prices = QLabel("DKP:"), QLabel("name:"), QLabel(
            "price:"), QLabel("digi price:"), QLabel("DKPC:"), QLabel("تعداد تنوع"), QLabel("prices:")
        self.product_name = QLineEdit()
        self.your_price = QLineEdit()
        self.price_on_digi = QLineEdit()
        self.DKP = QLineEdit()
        self.DKPC = QLineEdit()
        self.price_range = QLineEdit()
        self.price_range.setDisabled(True)
        self.variable = QComboBox()
        self.seller = QComboBox()
        self.warranty = QComboBox()
        self.mode = QComboBox()
        self.live_check = QCheckBox("live check")
        cancel, ok = QPushButton("Cancel"), QPushButton("OK")
        # placeholders
        self.product_name.setPlaceholderText("product name")
        self.your_price.setPlaceholderText("your price")
        self.price_on_digi.setPlaceholderText("digikala price")
        self.DKP.setPlaceholderText("DKP")
        self.DKPC.setPlaceholderText("DKPC")
        self.price_range.setPlaceholderText("prices")
        self.seller.setPlaceholderText("seller")
        self.variable.setPlaceholderText("variable")
        self.warranty.setPlaceholderText("Warranty")
        self.mode.setPlaceholderText("mode")
        self.mode.addItems(["Custom", "Low", "High", "By Box"])
        self.mode.setCurrentText("Low")
        # signals
        self.live_check.toggled.connect(self.check_dkp)
        self.DKP.textChanged.connect(self.check_dkp)
        self.your_price.textChanged.connect(self.fill_your_price)
        self.seller.currentTextChanged.connect(self.seller_changed)
        self.variable.currentTextChanged.connect(self.variable_changed)
        self.warranty.currentTextChanged.connect(self.warranty_changed)
        self.mode.currentTextChanged.connect(self.mode_changed)
        cancel.clicked.connect(self.cancel_button)
        ok.clicked.connect(self.ok_button)
        # layout
        layout.addWidget(dkp, 0, 0)
        layout.addWidget(self.live_check, 0, 2)
        layout.addWidget(self.DKP, 0, 1)
        layout.addWidget(name, 1, 0)
        layout.addWidget(self.product_name, 1, 1)
        layout.addWidget(self.count, 1, 2)
        layout.addWidget(price, 2, 0)
        layout.addWidget(self.your_price, 2, 1)
        layout.addWidget(self.seller, 2, 2)
        layout.addWidget(digi_price, 3, 0)
        layout.addWidget(self.price_on_digi, 3, 1)
        layout.addWidget(self.variable, 3, 2)
        layout.addWidget(dkpc, 4, 0)
        layout.addWidget(self.DKPC, 4, 1)
        layout.addWidget(self.warranty, 4, 2)
        layout.addWidget(self.prices, 5, 0)
        layout.addWidget(self.price_range, 5, 1)
        layout.addWidget(self.mode, 5, 2)

        layout.addWidget(cancel, 6, 1)
        layout.addWidget(ok, 6, 2)
        self.setLayout(layout)
        self.show()

    def clear_views(self):
        self.variable.clear()
        self.warranty.clear()
        self.seller.clear()

    def check_dkp(self):
        self.clear_views()
        dkp = self.DKP.text()
        if self.live_check.isChecked():
            if str(dkp).isdigit():
                # get product data
                status, self.variants, name = api.get_data(dkp)
                self.product_name.setText(name)
                if isinstance(self.variants, pandas.DataFrame):
                    self.bybox = self.variants.iloc[0]
                    self.variants = self.variants.sort_values(by="price")
                    # user Selection part
                    self.lowest = self.variants.iloc[0]
                    self.highest = self.variants.iloc[-1]

                    self.variable.addItems(self.variants["variable"].unique())
                    self.seller.addItems(self.variants["seller"].unique())
                    self.count.setText(f"{len(self.variants)} تنوع")
                    self.mode_changed(self.mode.currentText())
                    from_, til = util.add_comma(self.lowest["price"]), util.add_comma(self.highest["price"])
                    self.price_range.setText(f"{from_} to {til}")
                else:
                    self.DKPC.setText(status)
            else:
                pass

    def mode_changed(self, mode):
        if mode == "Low":
            self.fill_data(self.lowest)
        elif mode == "High":
            self.fill_data(self.highest)
        elif mode == "By Box":
            self.fill_data(self.bybox)
        elif mode == "Custom":
            pass

    def fill_data(self, variant):
        self.variable.setCurrentText(variant["variable"])
        self.seller.setCurrentText(variant["seller"])
        self.price_on_digi.setText(util.add_comma(variant["price"]))
        self.DKPC.setText(str(variant["id"]))
        self.warranty.setCurrentText(variant["warranty"])

    def filter(self, seller=None, variable=None, warranty=None):
        v = self.variants
        if seller and variable and warranty:
            return v.loc[(v["seller"] == seller) & (v["variable"] == variable) & (v["warranty"] == warranty)]
        if seller and variable:
            return v.loc[(v["seller"] == seller) & (v["variable"] == variable)]
        if seller and warranty:
            return v.loc[(v["seller"] == seller) & (v["warranty"] == warranty)]
        if variable and warranty:
            return v.loc[(v["variable"] == variable & (v["warranty"] == warranty))]
        if seller:
            return v.loc[v["seller"] == seller]
        if variable:
            return v.loc[v["variable"] == variable]
        if warranty:
            return v.loc[v["warranty"] == warranty]

    def seller_changed(self, seller):
        variant = self.filter(seller=seller)
        dkpc, variables, warranties = variant["id"], variant["variable"], variant["warranty"]
        self.variable.clear()
        self.warranty.clear()

        self.variable.addItems(variables.unique())
        self.warranty.addItems(warranties.unique())
        self.variable.setCurrentIndex(0)
        self.warranty.setCurrentIndex(0)
        self.DKPC.setText(str(dkpc.to_list()[0]))
        variable = self.variable.currentText()
        warranty = self.warranty.currentText()
        price = self.filter(seller=seller, variable=variable, warranty=warranty)["price"].to_list()[0]
        self.price_on_digi.setText(util.add_comma(price))
        if not price == self.lowest["price"] and not price == self.highest["price"]:
            self.mode.setCurrentText("custom")

    def variable_changed(self, variable):
        if self.seller.currentText():
            seller = self.seller.currentText()
            variant = self.filter(seller=seller, variable=variable)
            if len(variant) == 1:
                price = variant["price"]
                self.price_on_digi.setText(util.add_comma(price.to_list()[0]))
            else:
                pass

    def warranty_changed(self, warranty):
        variable = self.variable.currentText()
        seller = self.seller.currentText()
        variant = self.filter(warranty=warranty, variable=variable, seller=seller)
        if len(variant) == 1:
            price = variant["price"]
            self.price_on_digi.setText(util.add_comma(price.to_list()[0]))
        else:
            pass

    def cancel_button(self):
        self.close()

    def ok_button(self):
        db.add(db.Product(DKP=int(self.DKP.text()), name=self.product_name.text()))
        self.close()

    def fill_your_price(self, price):
        self.your_price.setText(util.add_comma(f"{int(price):,}"))


class Monitor(QWidget):
    def __init__(self):
        super().__init__()
        self.table = QTableWidget()
        self.table.setRowCount(10)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["DKP", "name", "my sell price", "digi sell price"])

        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.table)
        self.setLayout(self.vBox)
        self.show()

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

        self.add_product()

    def add_product(self):
        dialog = AddProduct()
        dialog.exec()
        self.monitor.refresh()


window = MainWindow()
window.show()
sys.exit(app.exec())
