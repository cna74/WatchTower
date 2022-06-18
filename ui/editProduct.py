from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QCheckBox, QPushButton, QGridLayout


class EditProduct(QDialog):
    def __init__(self):
        super(EditProduct, self).__init__()
        grid = QGridLayout()
        g = QGridLayout()
        label_name, label_price = QLabel("Name"), QLabel("Price")
        self.name, self.price = QLineEdit(), QLineEdit()
        self.check = QCheckBox("Fix Name")
        cancel, save = QPushButton("Cancel"), QPushButton("Save")
        g.addWidget(self.name, 0, 0)
        g.addWidget(self.check, 0, 1)
        grid.addWidget(label_name, 0, 0)
        grid.addLayout(g, 0, 1)
        # grid.addWidget(self.name, 0, 1)
        # grid.addWidget(self.check, 0, 2)
        grid.addWidget(label_price, 1, 0)
        grid.addWidget(self.price, 1, 1)
        grid.addWidget(cancel, 2, 0)
        grid.addWidget(save, 2, 1)
        self.setLayout(grid)
        self.show()
