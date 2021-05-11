# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import asyncio

from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPropertyAnimation, Qt, QThread, pyqtSignal

import utils
import static
import component


class OrderbookWorker(QThread):
    dataSent = pyqtSignal(component.Coin)

    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.alive = False

    def run(self):
        self.alive = True
        while self.alive:
            time.sleep(0.25)
            self.dataSent.emit(static.chart.coins[self.ticker])

    def close(self):
        self.alive = False
        super().terminate()


class OrderbookWidget(QWidget):
    def __init__(self, parent=None, ticker="KRW-BTC"):
        super().__init__(parent)
        uic.loadUi(utils.get_file_path("styles/ui/orderbook.ui"), self)

        #화면 수직,수평으로 늘릴 경우 칸에 맞게 변경됨
        #사용 가능한 공간을 채우기 위해 섹션의 크기를 자동으로 조정
        #참고 QHeaderView Class
        self.tableAsks.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableBids.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableAsks.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableBids.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ticker = ticker

        self.asksAnim = []
        self.bidsAnim = []

        self.bid_items = {}
        self.ask_items = {}
        for i in range(self.tableBids.rowCount()):
            # 매도호가
            self.bid_items[i] = (QTableWidgetItem(),
                                 QProgressBar(self.tableBids))
            self.bid_items[i][0].setTextAlignment(Qt.AlignVCenter)
            self.tableBids.setItem(i, 0, self.bid_items[i][0])
            self.bid_items[i][1].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.bid_items[i][1].setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0%);border : 1}
                QProgressBar::Chunk {background-color : rgba(0, 255, 0, 40%);border : 1}
            """)
            self.tableBids.setCellWidget(i, 1, self.bid_items[i][1])

            anim = QPropertyAnimation(self.bid_items[i][1], b"value")
            anim.setDuration(100)
            self.bidsAnim.append(anim)

            # 매수호가
            self.ask_items[i] = (QTableWidgetItem(
                str("")), QProgressBar(self.tableAsks))
            self.ask_items[i][0].setTextAlignment(Qt.AlignVCenter)
            self.tableAsks.setItem(i, 0, self.ask_items[i][0])
            self.ask_items[i][1].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.ask_items[i][1].setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0%);border : 1}
                QProgressBar::Chunk {background-color : rgba(255, 0, 0, 50%);border : 1}
            """)
            self.tableAsks.setCellWidget(i, 1, self.ask_items[i][1])

            anim = QPropertyAnimation(self.ask_items[i][1], b"value")
            anim.setDuration(100)
            self.asksAnim.append(anim)

        self.ow = OrderbookWorker(self.ticker)
        self.ow.dataSent.connect(self.updateData)
        self.ow.start()

        self.color_white = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        self.color_yellow = QtGui.QBrush(QtGui.QColor(255, 255, 0))

    def updateData(self, coin):
        try:
            data = coin.get_orderbook_units()[0:10] # 15개의 데이터를 10개로 자름
            asks_size = sum([x['as'] for x in data])
            bids_size = sum([x['bs'] for x in data])
            current_price = coin.get_trade_price()

            #self.tableAsks.setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            for i in range(len(data)):
                self.ask_items[i][0].setText(f"{data[9-i]['ap']:,.3f}")
                if data[9-i]['ap'] == current_price:  # 현재가
                    self.ask_items[i][0].setForeground(self.color_yellow)
                else:
                    self.ask_items[i][0].setForeground(self.color_white)
                # 범위가 int형으로 들어가기 때문에(값이 낮아서 전부 0으로 되는 문제)
                # 소수 3째자리 까지 표현하므로 범위값에 1000을 곱해서 범위를 지정해줌
                self.ask_items[i][1].setRange(0, 100)
                self.ask_items[i][1].setFormat(f"{data[9-i]['as']:,.3f}")

                self.bid_items[i][0].setText(f"{data[i]['bp']:,.3f}")
                if data[i]['bp'] == current_price:
                    self.bid_items[i][0].setForeground(self.color_yellow)
                else:
                    self.bid_items[i][0].setForeground(self.color_white)

                self.bid_items[i][1].setRange(0, 100)
                self.bid_items[i][1].setFormat(f"{data[i]['bs']:,.3f}")

                ask_range = data[9-i]['as'] * 100 / asks_size 
                bid_range = data[i]['bs'] * 100 / bids_size
                self.bidsAnim[i].setStartValue(bid_range)
                self.bidsAnim[i].setEndValue(bid_range)
                self.asksAnim[i].setStartValue(ask_range)
                self.asksAnim[i].setEndValue(ask_range)
                self.bidsAnim[i].start()
                self.asksAnim[i].start()
        except ValueError:
            return

    def closeEvent(self, event):
        self.ow.close()


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
    ow = OrderbookWidget()
    ow.show()
    exit(app.exec_())
