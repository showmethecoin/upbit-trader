# !/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import asyncio as aio

import aiopyupbit
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

from utils import get_file_path
from component import Account
from window_main import MainWindow
import static


class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(get_file_path('styles/ui/login.ui'), self)

        fontDB = QFontDatabase()
        fontDB.addApplicationFont(get_file_path('styles/fonts/MASQUE.ttf'))
        self.label.setFont(QFont('MASQUE', 55))
        self.label_2.setFont(QFont('gulim', 45))
        self.status = 0
        self.pushButton_connect.clicked.connect(self.change_page)
        self.msg = QMessageBox()
        self.load_config()
        # Set Titlebar button Click Event
        self.close_btn.clicked.connect(self.close_btn_click)
        self.minimize_btn.clicked.connect(lambda: self.showMinimized())
        self.maximize_btn.clicked.connect(lambda: self.maximize_restore())
        self.setWindowFlag(Qt.FramelessWindowHint)

        # MouseLeftClick Event Listener
        def mousePressEvent(event):
            if event.buttons() == Qt.LeftButton:
                self.dragPos = event.globalPos()
                event.accept()

        # MouseClickMove Event Listener
        def moveWindow(event):
            # IF MAXIMIZED CHANGE TO NORMAL
            if self.status == 1:
                self.status = 0
                self.showNormal()
            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        # DoubleClick Event Listener
        def doubleClickMaximizeRestore(event):
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                self.maximize_restore()

        # Link events to Titlebar
        self.toplabel_title.mousePressEvent = mousePressEvent
        self.toplabel_title.mouseMoveEvent = moveWindow
        self.toplabel_title.mouseDoubleClickEvent = doubleClickMaximizeRestore

    def close_btn_click(self):
        self.close()
        if static.chart != None:
            static.chart.stop()

    # Maximize Control Function
    def maximize_restore(self):
        if self.status == 0:
            self.showMaximized()
            self.status = 1
        else:
            self.status = 0
            self.showNormal()

    # Change to Main
    def change_page(self):
        try:
            static.account = Account(access_key=self.lineEdit_access.text(),
                                     secret_key=self.lineEdit_secret.text())
            result, _ = aio.run(static.account.upbit.check_authentication())
            if result:
                static.account.start()
                if(self.checkBox_save_user.isChecked()):
                    self.save_config()
                self.secondWindow = MainWindow()
                self.secondWindow.show()
                self.close()
        except Exception as e:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.autoFillBackground()
            self.msg.setWindowTitle('Authentication error')
            self.msg.setText(f'{e}')
            self.msg.show()

    # Save config
    def save_config(self):
        static.config.upbit_access_key = self.lineEdit_access.text()
        static.config.upbit_secret_key = self.lineEdit_secret.text()
        static.config.save()

    # Load config and read
    def load_config(self):
        self.lineEdit_access.setText(static.config.upbit_access_key)
        self.lineEdit_secret.setText(static.config.upbit_secret_key)


def gui_main():
    app = QApplication(sys.argv)
    GUI = LoginWidget()
    GUI.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    from component import RealtimeManager
    from utils import set_windows_selector_event_loop_global
    from config import Config
    
    set_windows_selector_event_loop_global()

    static.config = Config()
    static.config.load()

    loop = aio.new_event_loop()
    aio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=static.FIAT, contain_name=True))
    static.chart = RealtimeManager(codes=codes)
    static.chart.start()

    app = QApplication(sys.argv)
    GUI = LoginWidget()
    GUI.show()
    sys.exit(app.exec_())
