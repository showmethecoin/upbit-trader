# !/usr/bin/python
# -*- coding: utf-8 -*-
import math
import asyncio as aio
from ui_userinfo import Ui_Form
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import static


class UserinfoWorker(QThread):
    def __init__(self, object):
        super().__init__()
        self.alive = False
        self.view = object

    def run(self) -> None:
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        loop.run_until_complete(self.__loop())

    def terminate(self) -> None:
        self.alive = False
        return super().terminate()

    async def __loop(self):
        while self.alive:
            try:
                await aio.sleep(0.5)
                self.view.userdata1.setText(
                    f'{int(static.account.get_cash()):,}')
                self.view.userdata2.setText(
                    f'{math.ceil(static.account.get_buy_price()):,}')
                self.view.userdata3.setText(
                    f'{math.floor(static.account.get_evaluate_price()):,}')
                self.view.userdata4.setText(
                    f'{round(static.account.get_evaluate_price() + static.account.get_cash()):,}')
                self.view.userdata5.setText(
                    f'{round(static.account.get_total_loss()):,}')
                self.view.userdata6.setText(
                    f'{static.account.get_total_yield():.2f}')

                if int(static.account.get_total_loss()) < 0:
                    self.view.userdata5.setStyleSheet("Color : #CF304A")
                elif int(static.account.get_total_loss()) == 0:
                    self.view.userdata5.setStyleSheet("Color : white")
                else:
                    self.view.userdatat5.setStyleSheet("Color : #02C076")

                if static.account.get_total_yield() < 0:
                    self.view.userdata6.setStyleSheet("Color : #CF304A")
                elif static.account.get_total_yield() == 0:
                    self.view.userdata6.setStyleSheet("Color : white")
                else:
                    self.view.userdatat6.setStyleSheet("Color : #02C076")

            except Exception:
                pass


class UserinfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = Ui_Form()
        self.view.setupUi(self)
        self.uw = UserinfoWorker(self.view)
        
    # close thread
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.uw.close()
        return super().closeEvent(a0)


if __name__ == "__main__":
    import sys
    import aiopyupbit
    from config import Config
    from component import RealtimeManager, Account
    from utils import set_windows_selector_event_loop_global

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
    GUI = UserinfoWidget()
    GUI.show()
    sys.exit(app.exec_())
