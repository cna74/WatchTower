from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QCheckBox, QPushButton, QGridLayout, QApplication
import sys

import db
import util


class EditProduct(QDialog):
    def __init__(self):
        super(EditProduct, self).__init__()
        self.setWindowTitle("Edit Product")
        self.product = None
        grid = QGridLayout()
        g = QGridLayout()
        label_name, label_original_name, label_price = QLabel("Name"), QLabel("original name"), QLabel("Price")
        self.name, self.original_name, self.price = QLineEdit(), QLineEdit(), QLineEdit()
        self.price.textChanged.connect(self.price_changed)
        self.original_name.setDisabled(True)
        self.check = QCheckBox("Fix Name")
        cancel, save = QPushButton("Cancel"), QPushButton("Save")
        self.name.textChanged.connect(self.name_changed)
        self.check.toggled.connect(self.fix_name_changed)
        cancel.clicked.connect(self.cancel_clicked)
        save.clicked.connect(self.save_clicked)
        grid.addWidget(label_original_name, 0, 0)
        grid.addWidget(self.original_name, 0, 1)
        g.addWidget(self.name, 1, 0)
        g.addWidget(self.check, 1, 1)
        grid.addWidget(label_name, 1, 0)
        grid.addLayout(g, 1, 1)
        grid.addWidget(label_price, 2, 0)
        grid.addWidget(self.price, 2, 1)
        grid.addWidget(cancel, 3, 0)
        grid.addWidget(save, 3, 1)
        self.setLayout(grid)
        self.show()

    def save_clicked(self):
        self.product.fix_name = self.check.isChecked()
        self.product.name = self.name.text()
        self.product.my_sell_price = int(util.remove_comma(self.price.text()))
        db.edit(self.product)
        self.close()

    def cancel_clicked(self):
        self.close()

    def fix_name_changed(self):
        if not self.check.isChecked():
            self.name.setText(self.original_name.text())

    def name_changed(self):
        if self.name == self.original_name:
            self.check.setChecked(False)
        else:
            self.check.setChecked(True)

    def price_changed(self, price):
        self.price.setText(util.add_comma(price))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditProduct()
    window.show()
    sys.exit(app.exec())
