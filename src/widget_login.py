# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import jwt
import uuid
import requests

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

from window_main import MainWindow


class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('./src/styles/ui/login.ui', self)

        self.status = 0
        self.pushButton_connect.clicked.connect(self.change_page)
        self.msg = QMessageBox()
        self.read_save()
        # Set Titlebar button Click Event
        self.close_btn.clicked.connect(lambda: self.close())
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
        if self.check_authentication():
            if(self.checkBox_save_user.isChecked()):
                self.set_save()
            self.secondWindow = MainWindow()
            self.secondWindow.show()
            self.close()

    # Check Key
    def check_authentication(self):
        access_key = self.lineEdit_access.text()
        secret_key = self.lineEdit_secret.text()
        server_url = 'https://api.upbit.com'

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        # Rest Request
        res = requests.get(server_url + "/v1/accounts", headers=headers)

        # Check Error
        if res.text.find("error") != -1:
            # show Error Message Box
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.autoFillBackground()
            self.msg.setWindowTitle('Authentication error')
            self.msg.setText('Error : ' + res.json()['error']['name'])
            self.msg.show()
            return False
        else:
            return True

    # Make Save File
    def set_save(self):
        with open('.save.txt', 'w') as f:
            f.write(self.lineEdit_access.text() + '\n')
            f.write(self.lineEdit_secret.text())

    # Read Save File
    def read_save(self):
        if os.path.isfile('.save.txt'):
            with open('.save.txt', 'r') as f:
                line = f.readline().strip('\n')
                self.lineEdit_access.setText(line)
                line = f.readline()
                self.lineEdit_secret.setText(line)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    GUI = LoginWidget()
    GUI.show()
    #Page = SecondPage()
    sys.exit(app.exec_())
