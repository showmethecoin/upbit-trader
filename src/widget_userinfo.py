# !/usr/bin/python
# -*- coding: utf-8 -*-
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


class UserinfoWorker(QThread):
    def __init__(self, object):
        super().__init__()
        self.alive = False
        self.view = object

    def run(self) -> None:
        self.alive = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__loop())

    def terminate(self) -> None:
        self.alive = False
        return super().terminate()
    
    async def __loop(self):
        while self.alive:
            try:
                await asyncio.sleep(0.5)
                self.view.userdata1.setText(f'{int(static.account.get_cash()):,}')
                self.view.userdata2.setText(f'{int(static.account.get_buy_price()):,}')
                self.view.userdata3.setText(f'{int(static.account.get_evaluate_price()):,}')
                self.view.userdata4.setText(f'{int(static.account.get_evaluate_price()):,}')
                self.view.userdata5.setText(f'{int(static.account.get_total_loss()):,}')
                self.view.userdata6.setText(f'{static.account.get_total_yield():.2f}')
                
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

            except Exception as e:
                #log.error(e)
                pass


class UserinfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.uw = UserinfoWorker(uic.loadUi(utils.get_file_path("styles/ui/userinfo.ui"), self))
        self.uw.start()
        
    # close thread
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.uw.close()
        return super().closeEvent(a0)
        
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
    GUI = UserinfoWidget()
    GUI.show()
    sys.exit(app.exec_())
