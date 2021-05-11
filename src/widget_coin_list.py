# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import asyncio

from PyQt5 import uic
from PyQt5.QtWidgets import QAbstractItemDelegate, QHeaderView, QTableWidgetItem, QWidget, QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import utils
import static
import component
from widget_orderbook import OrderbookWorker


class ChartWorker(QThread):
    dataSent = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.alive = False

    def run(self):
        self.alive = True
        while self.alive:
            time.sleep(0.25)
            self.dataSent.emit(static.chart.coins.values())

    def close(self):
        self.alive = False
        super().terminate()


class CoinlistWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(utils.get_file_path("styles/ui/coin_list.ui"), self)

        #화면 수직,수평으로 늘릴 경우 칸에 맞게 변경됨
        #사용 가능한 공간을 채우기 위해 섹션의 크기를 자동으로 조정
        #참고 QHeaderView Class
        self.coin_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.coin_list.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.coin_list.horizontalHeader().setFixedHeight(40)
        count_codes = len(static.chart.codes)
        self.coin_list.setRowCount(count_codes)
        self.items = {}
        for i in range(count_codes):
            self.items[i] = (QTableWidgetItem(), QTableWidgetItem(), QTableWidgetItem())
            self.items[i][0].setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.items[i][1].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.items[i][2].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)  
            self.coin_list.setItem(i, 0, self.items[i][0])            
            self.coin_list.setItem(i, 1, self.items[i][1])
            self.coin_list.setItem(i, 2, self.items[i][2])

        self.cw = ChartWorker()
        self.cw.dataSent.connect(self.updataData)
        self.cw.start()

        self.coin_list.horizontalHeader().sectionClicked.connect(self.chkTopClicked)
        self.coin_list.cellClicked.connect(self.chkItemClicked)
        self.order = None
        self.chart = None

        self.color_red = QBrush(QColor(21, 125, 25))
        self.color_green = QBrush(QColor(241, 3, 3))
        self.color_white = QBrush(QColor(255, 255, 255))

    def updataData(self, data):
        for i, coin in enumerate(data):
            change_rate = coin.get_signed_change_rate()
            self.items[i][0].setText(f'{coin.korean_name}({coin.code[4:]})')
            self.items[i][1].setText(f'{coin.get_trade_price():,}')
            self.items[i][2].setText(f'{change_rate * 100:.2f} %')
            if change_rate < 0:
                self.items[i][1].setForeground(self.color_red)
                self.items[i][2].setForeground(self.color_red)
            elif change_rate > 0:
                self.items[i][1].setForeground(self.color_green)
                self.items[i][2].setForeground(self.color_green)
            else:
                self.items[i][1].setForeground(self.color_white)
                self.items[i][2].setForeground(self.color_white)
                
    def closeEvent(self):
        self.cw.close()

    def setOrder(self, order):
        self.order = order

    def setChart(self, chart):
        self.chart = chart

    def setTrade(self, trade):
        self.trade = trade

    def chkItemClicked(self):
        if len(self.coin_list.selectedItems()) == 0:
            return
        coin = f"KRW-{self.coin_list.selectedItems()[0].text().split('(')[1][:-1]}"
        self.order.ow.close()
        self.order.ow.wait()
        self.order.ow = OrderbookWorker(coin)
        self.order.ow.dataSent.connect(self.order.updateData)
        self.order.ow.start()
        # self.chart.coin = coin
        self.trade.set_price(coin)

    def chkTopClicked(self, topIndex):
        # 정렬 누르면 선택된 것이있으면 없애고 정렬
        self.coin_list.clearSelection()
        if topIndex == 0:
            static.chart.sort(target='code')
        elif topIndex == 1:
            static.chart.sort(target='value')
        else:
            static.chart.sort(target='change')


if __name__ == "__main__":
    import sys
    import aiopyupbit
    import config

    utils.set_windows_selector_event_loop_global()

    # Upbit coin chart
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=config.FIAT, contain_name=True))
    static.chart = component.RealtimeManager(codes=codes)
    static.chart.start()

    app = QApplication(sys.argv)
    cw = CoinlistWidget()
    cw.show()
    exit(app.exec_())
