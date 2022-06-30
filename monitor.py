from PyQt6.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QFont, QBrush
from PyQt6 import QtCore, QtGui
import editProduct
import webbrowser
import util
import db


class Monitor(QWidget):
    def __init__(self, category=None):
        super().__init__()
        # no fix_name and bybox
        self.category = category
        self.headers: list = (db.Product.__table__.columns.keys()[:-1])
        self.headers.append("Link")
        self.headers.remove("bybox")
        self.headers.remove("high")
        # self.setMouseTracking(True)
        self.table = QTableWidget(1, len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.table.cellDoubleClicked.connect(self.edit_product)
        self.table.cellClicked["int", 'int'].connect(self.open_page)
        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.table)
        self.setLayout(self.vBox)
        self.show()

    def remove_product(self):
        dkps = []
        for row in range(self.table.rowCount()):
            dkp = self.table.item(row, 0)
            if dkp.checkState() == QtCore.Qt.CheckState.Checked:
                dkps.append(dkp)
        for d in dkps:
            db.remove(int(d.text()))
        self.reload()

    def clear(self):
        rows = self.table.rowCount()
        for row in range(rows):
            self.table.removeRow(0)

    def reload(self):
        self.clear()
        self.table.setHorizontalHeaderLabels(self.headers)
        data = db.get_products(category=self.category)
        if len(data) > self.table.rowCount():
            self.table.setRowCount(len(data))
        for row, product in enumerate(data, start=0):
            for column, header in enumerate(self.headers):
                if header in ("bybox", "low", "high", "my_sell_price"):
                    self.table.setItem(row, column, QTableWidgetItem(str(util.add_comma(product.__dict__[header]))))
                    if header == "my_sell_price":
                        price = product.__dict__[header]
                        digi_low = product.__dict__["low"]
                        item = self.table.item(row, column)
                        if price < digi_low:
                            # red
                            brush = QBrush(QtGui.QColor("#ff0000"))
                        elif price > digi_low:
                            # 10% higher
                            if price > digi_low + ((digi_low / 100) * 10):
                                brush = QBrush(QtGui.QColor("#3ffc00"))
                            # 5% higher
                            elif price > digi_low + ((digi_low / 100) * 5):
                                brush = QBrush(QtGui.QColor("#97fc00"))
                            else:
                                brush = QBrush(QtGui.QColor("#dbfc00"))
                        elif digi_low - ((digi_low / 100) * 10) < price < digi_low + ((digi_low / 100) * 10):
                            brush = QBrush(QtGui.QColor("#ff6c00"))
                        else:
                            brush = QBrush(QtGui.QColor(0, 0, 0))
                        item.setForeground(brush)
                elif header == "DKP":
                    item = QTableWidgetItem(str(product.__dict__[header]))
                    item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                    self.table.setItem(row, column, item)
                elif header == "Link":
                    item = QTableWidgetItem("Open Page")
                    brush = QBrush(QtGui.QColor("#2b85c1"))
                    item.setForeground(brush)
                    font = QFont()
                    font.setBold(True)
                    font.setUnderline(True)
                    item.setFont(font)
                    self.table.setItem(row, column, item)
                else:
                    self.table.setItem(row, column, QTableWidgetItem(str(product.__dict__[header])))

        self.table.horizontalHeader().setSectionResizeMode(self.headers.index("name"),
                                                           QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(self.headers.index("category"),
                                                           QHeaderView.ResizeMode.ResizeToContents)

    def edit_product(self):
        edit_p = editProduct.EditProduct()
        dkp = self.table.item(self.table.currentRow(), self.headers.index("DKP")).text()
        name = self.table.item(self.table.currentRow(), self.headers.index("name")).text()
        price = self.table.item(self.table.currentRow(), self.headers.index("my_sell_price")).text()
        product: db.Product = db.get_by_dkp(int(dkp))
        edit_p.product = product
        edit_p.name.setText(name)
        edit_p.original_name.setText(product.name)
        edit_p.price.setText(price)
        edit_p.check.setChecked(product.fix_name)
        edit_p.exec()
        self.reload()

    def open_page(self, x, y):
        if y == self.headers.index("Link"):
            dkp = self.table.item(x, 0).text()
            webbrowser.open(f"https://digikala.com/product/dkp-{dkp}")