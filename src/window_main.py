# !/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import *

import static
import component
from ui_main import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.status = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(QSize(1400, 900))
        # Set Titlebar button Click Event
        self.clicked_style = self.ui.home_btn.styleSheet()
        self.none_clicked_style = self.ui.user_btn.styleSheet()
        self.ui.close_btn.clicked.connect(self.close_btn_click)
        self.ui.minimize_btn.clicked.connect(lambda: self.showMinimized())
        self.ui.home_btn.clicked.connect(self.home_btn_click)
        self.ui.user_btn.clicked.connect(self.user_btn_click)
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

    def close_btn_click(self):
        self.close()
        if static.chart != None:
            static.chart.stop()

    def home_btn_click(self):
        self.ui.qStackedWidget.setCurrentIndex(0)
        self.ui.home_btn.setStyleSheet(self.clicked_style)
        self.ui.user_btn.setStyleSheet(self.none_clicked_style)

    def user_btn_click(self):
        self.ui.qStackedWidget.setCurrentIndex(1)
        self.ui.user_btn.setStyleSheet(self.clicked_style)
        self.ui.home_btn.setStyleSheet(self.none_clicked_style)


if __name__ == "__main__":
    import sys
    import aiopyupbit
    import config
    import utils
    
    utils.set_windows_selector_event_loop_global()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=config.FIAT, contain_name=True))
    static.chart = component.RealtimeManager(codes=codes)
    static.chart.start()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
