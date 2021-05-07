
import sys
import asyncio
import platform
from ui_main import Ui_MainWindow
from ui_trade import Ui_Form
import static
from component import Chart
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
        self.resize(QSize(1300,900))
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
    

    # NOTE Windows 운영체제 환경에서 Python 3.7+부터 발생하는 EventLoop RuntimeError 관련 처리
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
	    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    static.chart = Chart()
    static.chart.sync_start()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())