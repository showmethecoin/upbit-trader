# !/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio as aio
from widget_settings import SettingsWidget

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import *

import static
from ui_main import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.status = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(QSize(1500, 1000))
        # Set Titlebar button Click Event
        self.clicked_style = self.ui.home_btn.styleSheet()
        self.none_clicked_style = self.ui.user_btn.styleSheet()
        self.ui.close_btn.clicked.connect(self.close_btn_click)
        self.ui.minimize_btn.clicked.connect(lambda: self.showMinimized())
        self.ui.home_btn.clicked.connect(self.home_btn_click)
        self.ui.user_btn.clicked.connect(self.user_btn_click)
        self.ui.signal_btn.clicked.connect(self.signal_btn_click)
        self.ui.btn_settings.clicked.connect(self.settings_btn_click)
        
        self.home_worker = [
                            self.ui.orderbook_widget.ow, 
                            self.ui.coinlist_widget.cw, 
                            self.ui.trade_widget.tw, 
                            self.ui.chart_widget.cw, 
                            self.ui.holding_list_widget.hw]
        self.user_worker = [
                            self.ui.userinfo_widget.view.widget.pw, 
                            self.ui.detailholdinglist_widget.dw,
                            self.ui.userinfo_widget.uw]

        self.signal_worker = [self.ui.signal_list_widget.sw]
        self.thread_start(self.home_worker)
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
        if static.signal_manager != None:
            static.signal_manager.terminate()

    def home_btn_click(self):
        self.ui.home_btn.setStyleSheet(self.clicked_style)
        self.ui.user_btn.setStyleSheet(self.none_clicked_style)
        self.ui.signal_btn.setStyleSheet(self.none_clicked_style)
        if self.ui.qStackedWidget.currentIndex != 0:
            self.thread_start(self.home_worker)
            self.thread_stop(self.user_worker)
            self.thread_stop(self.signal_worker)
            self.ui.qStackedWidget.setCurrentIndex(0)

    def user_btn_click(self):
        self.ui.user_btn.setStyleSheet(self.clicked_style)
        self.ui.home_btn.setStyleSheet(self.none_clicked_style)
        self.ui.signal_btn.setStyleSheet(self.none_clicked_style)
        if self.ui.qStackedWidget.currentIndex != 1:
            self.thread_start(self.user_worker)
            self.thread_stop(self.home_worker)
            self.thread_stop(self.signal_worker)
            self.ui.qStackedWidget.setCurrentIndex(1)

    def signal_btn_click(self):
        self.ui.qStackedWidget.setCurrentIndex(2)
        self.ui.signal_btn.setStyleSheet(self.clicked_style)
        self.ui.user_btn.setStyleSheet(self.none_clicked_style)
        self.ui.home_btn.setStyleSheet(self.none_clicked_style)
        if self.ui.qStackedWidget.currentIndex != 2:
            self.thread_start(self.signal_worker)
            self.thread_stop(self.home_worker)
            self.thread_stop(self.user_worker)
            self.ui.qStackedWidget.setCurrentIndex(2)
    
    def settings_btn_click(self):
        if static.settings_start == False:
            static.settings_start = True
            self.settings = SettingsWidget()
            self.settings.show()

    def thread_start(self, widgets):
        for w in widgets:
            w.start()
    def thread_stop(self, widgets):
        for w in widgets:
            w.alive = False


if __name__ == "__main__":
    import sys
    import aiopyupbit
    from config import Config
    from utils import set_windows_selector_event_loop_global
    from component import RealtimeManager, Account

    set_windows_selector_event_loop_global()

    static.config = Config()
    static.config.load()

    loop = aio.new_event_loop()
    aio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=static.FIAT, contain_name=True))
    static.chart = RealtimeManager(codes=codes)
    static.chart.start()

    # Upbit account
    static.account = Account(access_key=static.config.upbit_access_key,
                             secret_key=static.config.upbit_secret_key)
    static.account.start()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
