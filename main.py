from PyQt6.QtWidgets import QMainWindow, QApplication, QStatusBar, QLabel, QMenu, QTabWidget
from addProduct import AddProduct
from PyQt6.QtGui import QAction
from setting import Setting
from monitor import Monitor
from PyQt6 import QtCore
import threading
import datetime
import time
import util
import sys
import db

app = QApplication(sys.argv)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(900, 700)
        self.refresh_rate = util.configure()
        self.setWindowTitle("Digi Watchtower")
        self.tab = QTabWidget()
        self.tabs = []
        self.setup_tabs()
        self.setCentralWidget(self.tab)
        # menubar
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        add = self.fileMenu.addAction("Add product")
        add.triggered.connect(self.add_product)
        refresh = self.menuBar.addAction("Refresh")
        setting = self.menuBar.addAction("Setting")
        setting.triggered.connect(self.set_setting)
        refresh.triggered.connect(self.update_database)
        # context
        self.addproduct = QAction("Add Product", self)
        self.addproduct.triggered.connect(self.add_product)
        self.reload = QAction("Reload", self)
        self.reload.triggered.connect(self.reload_all_tabs)
        self.reload.setToolTip("it's free")
        self.update = QAction("Update now", self)
        self.update.setToolTip("cost requests")
        self.update.triggered.connect(self.update_database)
        self.clear = QAction("Clear Table", self)
        self.clear.triggered.connect(self.tab.currentWidget().clear)
        self.delete = QAction("Delete Selected")
        self.delete.triggered.connect(self.remove_selected)
        self.settings = QAction("Settings...")
        self.settings.triggered.connect(self.set_setting)
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
        self.reload_all_tabs()
        # thread
        self.stop_thread = False
        self.thread = threading.Thread(target=self.update_timer, args=(lambda: self.stop_thread,))
        self.thread.start()
        self.update_database()
        self.show()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_R:
            self.reload_all_tabs()
        elif event.key() == QtCore.Qt.Key.Key_Delete:
            self.remove_selected()
        else:
            pass

    def remove_selected(self):
        self.tab.currentWidget().remove_product()
        self.reload_all_tabs()

    def contextMenuEvent(self, event):
        context_menu = QMenu()
        context_menu.setToolTipsVisible(True)
        context_menu.addAction(self.addproduct)
        context_menu.addSeparator()
        context_menu.addAction(self.reload)
        context_menu.addAction(self.update)
        context_menu.addSeparator()
        context_menu.addAction(self.clear)
        context_menu.addAction(self.delete)
        context_menu.addSeparator()
        context_menu.addAction(self.settings)

        action = context_menu.exec(self.mapToGlobal(event.pos()))

    def update_database(self):
        db.update_all()
        self.last_update.setText(datetime.datetime.now().strftime("%X"))
        self.reload_all_tabs()

    def update_timer(self, stop_thread):
        delta = datetime.timedelta(minutes=self.refresh_rate)
        seconds = delta.seconds
        while True:
            for s in range(seconds, -1, -1):
                time.sleep(1)
                self.ETA.setText(str(datetime.timedelta(seconds=s)))
                if s == 0:
                    self.update_database()
                    break
                if stop_thread():
                    break
            if stop_thread():
                break

    def add_product(self):
        dialog = AddProduct()
        dialog.exec()
        self.setup_tabs()
        self.reload_all_tabs()

    def set_setting(self):
        s = Setting()
        s.refresh_interval.setValue(self.refresh_rate)
        s.exec()
        current_refresh_rate = self.refresh_rate
        self.refresh_rate = s.refresh_rate
        if not current_refresh_rate == self.refresh_rate:
            self.stop_thread = True
            self.thread.join()
            self.stop_thread = False
            self.thread = threading.Thread(target=self.update_timer, args=(lambda: self.stop_thread,))
            self.thread.start()

    def setup_tabs(self):
        tabs = db.get_categories()
        if not tabs == self.tabs:
            self.tab.clear()
            self.tabs = tabs
            self.tab.addTab(Monitor(), "All")
            for tab in tabs:
                self.tab.addTab(Monitor(category=tab), tab)

    def reload_all_tabs(self):
        self.setup_tabs()
        for tab_index in range(self.tab.count()):
            tab: Monitor = self.tab.widget(tab_index)
            tab.reload()

    def closeEvent(self, event) -> None:
        self.stop_thread = True
        self.thread.join()
        event.accept()


if __name__ == "__main__":
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
