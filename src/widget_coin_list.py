# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import asyncio

from PyQt5 import uic
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QWidget, QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import utils
import static
import component
from widget_orderbook import OrderbookWorker


class ChartWorker(QThread):
    dataSent = pyqtSignal(list)

    def __init__(self, coinlist):
        super().__init__()
        self.coinlist = coinlist
        self.alive = True

    def run(self):
        while self.alive:
            data = []
            cointradeprice = []
            coinchangerate = []
            for coin in static.chart.coins.values():
                #foramt(값, ",") 이거 1000단위로 , 찍어줌
                cointradeprice.append(
                    format(round(coin.get_trade_price(), 3), ","))
                coinchangerate.append(
                    round(coin.get_signed_change_rate() * 100, 2))
            data.append(self.coinlist)
            data.append(cointradeprice)
            data.append(coinchangerate)
            time.sleep(0.1)

            if data != None:
                self.dataSent.emit(data)

    def close(self):
        self.alive = False


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
        self.coinlist = static.chart.codes

        for i in range(len(self.coinlist)):
            item_0 = QTableWidgetItem(str(""))
            item_0.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.coin_list.setItem(i, 0, item_0)

            item_1 = QTableWidgetItem(str(""))
            item_1.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.coin_list.setItem(i, 1, item_1)

            item_2 = QTableWidgetItem(str(""))
            item_2.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.coin_list.setItem(i, 2, item_2)

        self.cw = ChartWorker(self.coinlist)
        self.cw.dataSent.connect(self.updataData)
        self.cw.start()

        self.coin_list.cellClicked.connect(self.chkItemClicked)
        self.order = None
        self.chart = None

    def updataData(self, data):
        for i in range(len(data[0])):
            item_0 = self.coin_list.item(i, 0)
            item_0.setText(str(data[0][i]))
            item_1 = self.coin_list.item(i, 1)
            item_1.setText(str(data[1][i]))
            item_2 = self.coin_list.item(i, 2)
            item_2.setText(str(data[2][i]))
            if data[2][i] < 0:
                item_1.setForeground(QBrush(QColor(21, 125, 25)))
                item_2.setForeground(QBrush(QColor(21, 125, 25)))
            elif data[2][i] > 0:
                item_1.setForeground(QBrush(QColor(241, 3, 3)))
                item_2.setForeground(QBrush(QColor(241, 3, 3)))

    def closeEvent(self, event):
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
        coin = self.coin_list.selectedItems()[0].text()
        self.order.ow.close()
        self.order.ow.wait()
        self.order.ow = OrderbookWorker(coin)
        self.order.ow.dataSent.connect(self.order.updateData)
        self.order.ow.start()
        self.chart.coin = coin
        self.trade.set_price(coin)


if __name__ == "__main__":
    import sys
    import aiopyupbit

    utils.set_windows_selector_event_loop_global()

    # Upbit coin chart
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=static.FIAT, contain_name=True))
    static.chart = component.RealtimeManager(codes=codes)
    static.chart.start()

    app = QApplication(sys.argv)
    cw = CoinlistWidget()
    cw.show()
    exit(app.exec_())
