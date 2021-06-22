# !/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio as aio
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import static
from utils import get_file_path


class SignallistWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(get_file_path("styles/ui/signal_list.ui"), self)
        self.signallist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


if __name__ == "__main__":
    import sys
    from component import RealtimeManager, Account
    from utils import set_windows_selector_event_loop_global
    import aiopyupbit
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

    # Upbit account
    static.account = Account(
        static.config.upbit_access_key, static.config.upbit_secret_key)
    static.account.start()

    app = QApplication(sys.argv)
    GUI = SignallistWidget()
    GUI.show()
    sys.exit(app.exec_())
