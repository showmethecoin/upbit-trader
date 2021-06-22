# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import asyncio as aio

from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

import static
from utils import get_file_path


class HoldingListWorker(QThread):
    dataSent = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.alive = False

    def run(self):
        self.alive = True
        while self.alive:
            time.sleep(0.5)
            self.dataSent.emit(static.account.coins)

    def close(self):
        self.alive = False
        return super().terminate()


class HoldingListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(get_file_path("styles/ui/holding_list.ui"), self)

        #참고 QHeaderView Class
        self.hold_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.hw = HoldingListWorker()
        self.hw.dataSent.connect(self.updateData)

        self.color_red = QBrush(QColor(207, 48, 74))  # CF304A
        self.color_green = QBrush(QColor(2, 192, 118))  # 02C076
        self.color_white = QBrush(QColor(255, 255, 255))

    def updateData(self, data):
        # data는 static.account.coins
        # 테이블 설정
        # 테이블을 처음 설정할 경우 또는 설정된 table row갯수와 set해야되는 data갯수가 다를 경우
        if self.hold_list.rowCount() != len(data):
            self.hold_list.clearContents()  # 테이블 지우고
            if len(data) == 0:
                return
            self.items = []
            # 동적으로 row관리
            count_codes = len(data)
            self.hold_list.setRowCount(count_codes)
            font = QFont()
            font.setBold(True)

            for i in range(count_codes):
                self.items.append([QTableWidgetItem(), QTableWidgetItem()])
                self.items[i][0].setFont(font)
                self.items[i][0].setTextAlignment(
                    Qt.AlignLeft | Qt.AlignVCenter)
                self.items[i][1].setFont(font)
                self.items[i][1].setTextAlignment(
                    Qt.AlignRight | Qt.AlignVCenter)
                self.hold_list.setItem(i, 0, self.items[i][0])
                self.hold_list.setItem(i, 1, self.items[i][1])
                
        for i, coin in enumerate(data):
            self.items[i][0].setText(static.chart.get_coin(f'{static.FIAT}-{coin}').korean_name + '(' + coin + ')')
            self.items[i][1].setText(f"{data[coin]['yield']:,.2f} %")
            if data[coin]['yield'] < 0:
                self.items[i][1].setForeground(self.color_red)
            elif data[coin]['yield'] > 0:
                self.items[i][1].setForeground(self.color_green)
            else:
                self.items[i][1].setForeground(self.color_white)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.hw.close()
        return super().closeEvent(a0)


if __name__ == "__main__":
    import sys
    from component import Account, RealtimeManager
    import aiopyupbit
    from utils import set_windows_selector_event_loop_global
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
    static.account = Account(access_key=static.config.upbit_access_key,
                             secret_key=static.config.upbit_secret_key)
    static.account.start()

    app = QApplication(sys.argv)
    GUI = HoldingListWidget()
    GUI.show()
    sys.exit(app.exec_())
