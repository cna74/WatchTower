from PyQt6.QtWidgets import QDialog, QGridLayout, QSpinBox, QLabel, QPushButton, QLineEdit
import util


class Setting(QDialog):
    def __init__(self):
        super(Setting, self).__init__()
        layout = QGridLayout()
        self.refresh_rate = util.configure()
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setValue(1)
        self.refresh_interval.minimum()
        remain = QLineEdit()
        remain.setReadOnly(True)
        cancel, ok, self.apply = QPushButton("Cancel"), QPushButton("OK"), QPushButton("Apply")
        cancel.clicked.connect(self.cancel_pressed)
        ok.clicked.connect(self.ok_pressed)
        self.apply.clicked.connect(self.apply_pressed)
        layout.addWidget(QLabel("refresh_interval_label"), 0, 0)
        layout.addWidget(self.refresh_interval, 0, 1)
        layout.addWidget(QLabel("minuet"), 0, 2)
        layout.addWidget(QLabel("remaining requests:"), 1, 0)
        layout.addWidget(remain, 1, 1)
        layout.addWidget(cancel, 2, 0)
        layout.addWidget(ok, 2, 1)
        layout.addWidget(self.apply, 2, 2)
        self.setLayout(layout)

    def cancel_pressed(self):
        self.close()

    def ok_pressed(self):
        refresh = int(self.refresh_interval.text())
        self.refresh_rate = util.configure(refresh)
        self.close()

    def apply_pressed(self):
        refresh = int(self.refresh_interval.text())
        self.refresh_rate = util.configure(refresh)
        self.apply.setDisabled(True)
