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
        
        self.ow = OrderbookWorker(ticker)
        self.ow.dataSent.connect(self.updateData)
        self.ow.start()

        self.asksAnim = []
        self.bidsAnim = []
        self.bid_items = []
        self.ask_items = []
        for i in range(self.tableBids.rowCount()):
            # 매도호가
            self.bid_items.append([QTableWidgetItem(), QProgressBar(self.tableBids), 0])
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
            self.ask_items.append([QTableWidgetItem(), QProgressBar(self.tableAsks), 0])
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

        self.color_white = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        self.color_yellow = QtGui.QBrush(QtGui.QColor(255, 255, 0))

    def updateData(self, coin):
        try:
            data = coin.get_orderbook_units()[0:10] 
            asks_size = sum([x['as'] for x in data])
            bids_size = sum([x['bs'] for x in data])
            current_price = coin.get_trade_price()
            for i in range(len(data)):
                
                self.bid_items[i][0].setText(f"{(lambda x: x if x < 100 else int(x))(data[i]['bp']):,}")
                self.bid_items[i][0].setForeground((lambda x: self.color_yellow if x == current_price else self.color_white)(data[i]['bp']))
                self.bid_items[i][1].setRange(0, 100)
                self.bid_items[i][1].setFormat(f"{data[i]['bs']:,.3f}")
                
                self.ask_items[i][0].setText(f"{(lambda x: x if x < 100 else int(x))(data[9-i]['ap']):,}")
                self.ask_items[i][0].setForeground((lambda x: self.color_yellow if x == current_price else self.color_white)(data[9-i]['ap']))
                self.ask_items[i][1].setRange(0, 100)
                self.ask_items[i][1].setFormat(f"{data[9-i]['as']:,.3f}")

                self.bidsAnim[i].setStartValue(self.bid_items[i][2])
                self.asksAnim[i].setStartValue(self.ask_items[i][2])
                self.bid_items[i][2] = (data[i]['bs'] / bids_size) * 100
                self.ask_items[i][2] = (data[9-i]['as'] / asks_size * 100)
                self.bidsAnim[i].setEndValue(self.bid_items[i][2])
                self.asksAnim[i].setEndValue(self.ask_items[i][2])
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
