from PyQt6.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox, QApplication
import util
import pandas
import inspect
import db
import sys


class AddProduct(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(500, 400)
        self.setWindowTitle("Add Product")
        self.current_variant = self.lowest = self.highest = self.bybox = self.variants = self.original_name = None
        layout = QGridLayout()
        row1 = QGridLayout()
        dkp, name, price, digi_price, dkpc, self.count, self.prices = QLabel("DKP:"), QLabel("name:"), QLabel(
            "price:"), QLabel("digi price:"), QLabel("DKPC:"), QLabel("تعداد تنوع"), QLabel("prices:")
        self.fix_name = QCheckBox("Fix Name")
        self.product_name = QLineEdit()
        self.category = None
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
        self.fix_name.toggled.connect(self.fix_name_toggled)
        self.product_name.textChanged.connect(self.product_name_changed)
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
        layout.addWidget(self.DKP, 0, 1)
        layout.addWidget(self.live_check, 0, 2)
        layout.addWidget(name, 1, 0)
        row1.addWidget(self.product_name, 0, 1)
        row1.addWidget(self.fix_name, 0, 2)
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
        layout.addLayout(row1, 1, 1)
        self.setLayout(layout)
        self.show()

    def clear_views(self):
        self.seller.clear()
        self.variable.clear()
        self.warranty.clear()

    def check_dkp(self):
        self.clear_views()
        dkp = self.DKP.text()
        if self.live_check.isChecked():
            if str(dkp).isdigit():
                # get product data
                status, self.variants, self.original_name, self.category = util.get_data(dkp)
                self.product_name.setText(self.original_name)
                if isinstance(self.variants, pandas.DataFrame):
                    self.bybox = self.variants.iloc[0]
                    self.variants = self.variants.sort_values(by="price")
                    # user Selection part
                    self.lowest = self.variants.iloc[0]
                    self.highest = self.variants.iloc[-1]

                    self.count.setText(f"{len(self.variants)} تنوع")
                    self.fill_data()
                    from_, til = util.add_comma(self.lowest["price"]), util.add_comma(self.highest["price"])
                    self.price_range.setText(f"{from_} to {til}")
                else:
                    # out of stock OR stop production
                    self.DKPC.setText(status)
            else:
                self.DKP.setText("")

    def mode_changed(self):
        self.fill_data()

    def filter(self, seller=None, variable=None, warranty=None) -> pandas.DataFrame:
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

    def fill_data(self, variant=None):
        try:
            self.clear_views()
            mode = self.mode.currentText()
            if isinstance(variant, pandas.DataFrame):
                seller, variable, warranty = variant["seller"].iloc[0], variant["variable"].iloc[0], \
                                             variant["warranty"].iloc[0]
                self.current_variant = self.filter(seller=seller, variable=variable, warranty=warranty).iloc[0]
                self.fill_data(variant=self.current_variant)

            else:
                if mode == "Low":
                    variant = self.lowest
                elif mode == "High":
                    variant = self.highest
                elif mode == "By Box":
                    variant = self.bybox

                self.current_variant = variant

                self.seller.addItems(self.variants["seller"].unique())
                self.variable.addItems(self.variants["variable"].unique())
                self.warranty.addItems(self.variants["warranty"].unique())

                if isinstance(variant, pandas.Series):
                    self.seller.setCurrentText(variant["seller"])
                    self.variable.setCurrentText(variant["variable"])
                    self.warranty.setCurrentText(variant["warranty"])
                    self.DKPC.setText(str(variant["id"]))
                    self.price_on_digi.setText(util.add_comma(variant["price"]))

        except Exception as E:
            print(f"{inspect.stack()[0][3]}, {inspect.stack()[1][3]}, {E}")

    def seller_changed(self, seller):
        try:
            if inspect.stack()[1][3] == "add_product":
                if not seller == self.current_variant["seller"]:
                    self.mode.setCurrentText("Custom")
                    variant = self.filter(seller=seller)
                    self.fill_data(variant=variant)
        except Exception as E:
            print(f"{inspect.stack()[0][3]}, {inspect.stack()[1][3]}, {E}")

    def variable_changed(self, variable):
        try:
            if inspect.stack()[1][3] == "<module>":
                if not variable == self.current_variant["variable"]:
                    self.mode.setCurrentText("Custom")
                    variant = self.filter(variable=variable)
                    self.fill_data(variant=variant)
        except Exception as E:
            print(f"{inspect.stack()[0][3]}, {inspect.stack()[1][3]}, {E}")

    def warranty_changed(self, warranty):
        try:
            if inspect.stack()[1][3] == "<module>":
                if not warranty == self.current_variant["warranty"]:
                    self.mode.setCurrentText("Custom")
                    variant = self.filter(warranty=warranty)
                    self.fill_data(variant=variant)
        except Exception as E:
            print(f"{inspect.stack()[0][3]}, {inspect.stack()[1][3]}, {E}")

    def cancel_button(self):
        self.close()

    def ok_button(self):
        dkp, category, name, fix_name = self.DKP.text(), self.category, self.product_name.text(), self.fix_name.isChecked()
        if isinstance(self.variants, pandas.DataFrame):
            bybox, low, high = self.bybox["price"], self.lowest["price"], self.highest["price"]
        else:
            bybox = low = high = 0

        if not self.your_price.text() == "":
            my_sell_price = util.remove_comma(self.your_price.text())
        else:
            my_sell_price = 0

        db.add(db.Product(DKP=int(dkp), category=category, name=name, bybox=int(bybox), low=int(low), high=int(high),
                          my_sell_price=int(my_sell_price), fix_name=fix_name))
        self.close()

    def fill_your_price(self, price):
        self.your_price.setText(util.add_comma(price))

    def product_name_changed(self):
        if self.original_name:
            if not self.product_name.text() == self.original_name:
                self.fix_name.setChecked(True)

    def fix_name_toggled(self):
        if self.fix_name.isCheckable() and self.original_name:
            self.product_name.setText(self.original_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddProduct()
    window.show()
    sys.exit(app.exec())
