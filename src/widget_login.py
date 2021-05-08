# !/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import yaml
import asyncio

from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from window_main import MainWindow
import aiopyupbit
import static


class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('./src/styles/ui/login.ui', self)

        self.status = 0
        self.pushButton_connect.clicked.connect(self.change_page)
        self.msg = QMessageBox()
        self.read_config()
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
        def dobleClickMaximizeRestore(event):
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                self.maximize_restore()

        # Link events to Titlebar
        self.toplabel_title.mousePressEvent = mousePressEvent
        self.toplabel_title.mouseMoveEvent = moveWindow
        self.toplabel_title.mouseDoubleClickEvent = dobleClickMaximizeRestore


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
        static.upbit = aiopyupbit.Upbit(self.lineEdit_access.text(), self.lineEdit_secret.text())
        result, message = asyncio.run(static.upbit.check_authentication())
        if result:
            if(self.checkBox_save_user.isChecked()):
                self.edit_config()
            # User upbit connection
            static.upbit = aiopyupbit.Upbit(
            self.lineEdit_access.text(), self.lineEdit_secret.text())
            self.secondWindow = MainWindow()
            self.secondWindow.show()
            self.close()
        else:
            # show Error Message Box
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.autoFillBackground()
            self.msg.setWindowTitle('Authentication error')
            self.msg.setText(f'Error : {message}')
            self.msg.show()

    # Edit Config File
    def edit_config(self):
        with open('./config.yaml', 'w') as file:
            self.config['UPBIT']['ACCESS_KEY'] = self.lineEdit_access.text()
            self.config['UPBIT']['SECRET_KEY'] = self.lineEdit_secret.text()
            yaml.dump(self.config, file)

    # Read Save File
    def read_config(self):
        with open('./config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
        self.lineEdit_access.setText(self.config['UPBIT']['ACCESS_KEY'])
        self.lineEdit_secret.setText(self.config['UPBIT']['SECRET_KEY'])

def gui_main():
    app = QApplication(sys.argv)
    GUI = LoginWidget()
    GUI.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    import component
    import sys
    # NOTE Windows 운영체제 환경에서 Python 3.7+부터 발생하는 EventLoop RuntimeError 관련 처리
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
	    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    app = QApplication(sys.argv)
    static.chart = component.RealtimeManager()
    static.chart.start()
    GUI = LoginWidget()
    GUI.show()
    sys.exit(app.exec_())
