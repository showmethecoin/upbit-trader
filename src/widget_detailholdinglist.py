# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import math
import asyncio as aio

from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

import static
from utils import get_file_path

class DetailholdinglistWorker(QThread):
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

class DetailholdinglistWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(get_file_path("styles/ui/detailholdinglist.ui"), self)

        #참고 QHeaderView Class
        self.detailholdinglist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.hold_list.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.color_red = QBrush(QColor(207, 48, 74))  # CF304A
        self.color_green = QBrush(QColor(2, 192, 118))  # 02C076
        self.color_white = QBrush(QColor(255, 255, 255))

        self.dw = DetailholdinglistWorker()
        self.dw.dataSent.connect(self.updateData)

    def updateData(self, data):
        # data는 static.account.coins
        # 테이블 설정
        # 테이블을 처음 설정할 경우 또는 설정된 table row갯수와 set해야되는 data갯수가 다를 경우
        if self.detailholdinglist.rowCount() != len(data):
            self.detailholdinglist.clearContents() # 테이블 지우고
            if len(data) == 0: 
                return
            self.items = []
            # 동적으로 row관리
            count_codes = len(data)
            self.detailholdinglist.setRowCount(count_codes)
            font = QFont()
            font.setBold(True)

            for i in range(count_codes):
                self.items.append([QTableWidgetItem(), QTableWidgetItem(), QTableWidgetItem(), QTableWidgetItem(), QTableWidgetItem(), QTableWidgetItem()])
                self.items[i][0].setFont(font)
                self.items[i][0].setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.items[i][1].setFont(font)
                self.items[i][1].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.items[i][2].setFont(font)
                self.items[i][2].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.items[i][3].setFont(font)
                self.items[i][3].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.items[i][4].setFont(font)
                self.items[i][4].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.items[i][5].setFont(font)
                self.items[i][5].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.detailholdinglist.setItem(i, 0, self.items[i][0])            
                self.detailholdinglist.setItem(i, 1, self.items[i][1])
                self.detailholdinglist.setItem(i, 2, self.items[i][2])
                self.detailholdinglist.setItem(i, 3, self.items[i][3])
                self.detailholdinglist.setItem(i, 4, self.items[i][4])
                self.detailholdinglist.setItem(i, 5, self.items[i][5])

        for i, coin in enumerate(data):
            self.items[i][0].setText(static.chart.get_coin(f'{static.FIAT}-{coin}').korean_name + '(' + coin + ')')
            self.items[i][1].setText(f"{data[coin]['balance'] + data[coin]['locked']:,.8f}")
            self.items[i][2].setText(f"{(lambda x: x if x < 100 else math.ceil(x))(data[coin]['avg_buy_price']):,}")
            self.items[i][3].setText(f"{math.ceil(data[coin]['purchase']):,}")
            self.items[i][4].setText(f"{math.floor(data[coin]['evaluate']):,}")
            self.items[i][5].setText(f"{data[coin]['yield']:,.2f}")
            if data[coin]['yield'] < 0 :
                self.items[i][5].setForeground(self.color_red)
            elif data[coin]['yield'] > 0 :
                self.items[i][5].setForeground(self.color_green)
            else:
                self.items[i][5].setForeground(self.color_white)  
             
    # close thread
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.dw.close()
        return super().closeEvent(a0)
    
if __name__ == "__main__":
    import sys
    from component import RealtimeManager, Account
    import aiopyupbit
    from config import Config
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
    GUI = DetailholdinglistWidget()
    GUI.show()
    sys.exit(app.exec_())
