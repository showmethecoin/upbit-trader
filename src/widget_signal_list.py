# !/usr/bin/python
# -*- coding: utf-8 -*-
import math
import asyncio
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import utils
from static import log
import static
import config


class SignallistWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(utils.get_file_path("styles/ui/signal_list.ui"), self)
        
        self.signallist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        
if __name__ == "__main__":
    import sys
    import component
    import aiopyupbit

    utils.set_windows_selector_event_loop_global()

    static.config = config.Config()
    static.config.load()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=static.FIAT, contain_name=True))
    static.chart = component.RealtimeManager(codes=codes)
    static.chart.start()
    
    # Upbit account
    static.account = component.Account(static.config.upbit_access_key, static.config.upbit_secret_key)
    static.account.sync_start()
    app = QApplication(sys.argv)
    GUI = SignallistWidget()
    GUI.show()
    sys.exit(app.exec_())
