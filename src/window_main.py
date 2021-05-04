
import sys
import asyncio
import platform
from ui_main import Ui_MainWindow
import ui_styles
from ui_trade import Ui_Form
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PyQt5.QtWidgets import *

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.status = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(QSize(1400,900))
        # Set Titlebar button Click Event
        self.ui.close_btn.clicked.connect(lambda: self.close())
        self.ui.minimize_btn.clicked.connect(lambda: self.showMinimized())
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
        
        # Link events to Titlebar
        self.ui.toplabel_title.mousePressEvent = mousePressEvent
        self.ui.toplabel_title.mouseMoveEvent = moveWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())