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
        self.size = 10
        self.ticker = ticker
        self.alive = True

    def run(self):
        while self.alive:
            time.sleep(0.3)
            if static.chart.coins[self.ticker] != None:
                self.dataSent.emit(static.chart.coins[self.ticker])

    def close(self):
        self.alive = False


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
        for i in range(self.tableBids.rowCount()):
            # 매도호가
            item_0 = QTableWidgetItem(str(""))
            item_0.setTextAlignment(Qt.AlignVCenter)
            self.tableAsks.setItem(i, 0, item_0)

            item_1 = QProgressBar(self.tableAsks)
            item_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_1.setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0%);border : 1}
                QProgressBar::Chunk {background-color : rgba(255, 0, 0, 50%);border : 1}
            """)
            self.tableAsks.setCellWidget(i, 1, item_1)
            anim = QPropertyAnimation(item_1, b"value")
            anim.setDuration(100)
            self.asksAnim.append(anim)

            # 매수호가
            item_0 = QTableWidgetItem(str(""))
            item_0.setTextAlignment(Qt.AlignVCenter)
            self.tableBids.setItem(i, 0, item_0)

            item_1 = QProgressBar(self.tableBids)
            item_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_1.setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0%);border : 1}
                QProgressBar::Chunk {background-color : rgba(0, 255, 0, 40%);border : 1}
            """)
            self.tableBids.setCellWidget(i, 1, item_1)
            anim = QPropertyAnimation(item_1, b"value")
            anim.setDuration(100)
            self.bidsAnim.append(anim)

        self.ow = OrderbookWorker(self.ticker)
        self.ow.dataSent.connect(self.updateData)
        self.ow.start()

    def updateData(self, coin):
        data = coin.get_orderbook_units()

        #15개의 데이터를 10개로 자름
        data = data[0:10]
        asks_size = coin.get_total_ask_size() * 0.01
        bids_size = coin.get_total_bid_size() * 0.01
        # 현재가, 호가창에서 현재가의 위치를 찍기위해 선언
        trade_price = coin.get_trade_price()

        #self.tableAsks.setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))

        for i in range(len(data)):
            item_0 = self.tableAsks.item(i, 0)
            item_0.setText(f"{round(data[9-i]['ap'],3):,}")
            item_1 = self.tableAsks.cellWidget(i, 1)
            if data[9-i]['ap'] == trade_price:
                item_0.setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
            else:
                item_0.setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            # 범위가 int형으로 들어가기 때문에(값이 낮아서 전부 0으로 되는 문제)
            # 소수 3째자리 까지 표현하므로 범위값에 1000을 곱해서 범위를 지정해줌
            item_1.setRange(0, 100)
            item_1.setFormat(f"{round(data[9-i]['as'],3):,}")

            item_0 = self.tableBids.item(i, 0)
            item_0.setText(f"{round(data[i]['bp'],3):,}")
            if data[i]['bp'] == trade_price:
                #item_0.setStyleSheet("border:1px solid grey; border-bottom-left-radius: 5px;border-bottom-right-radius: 5px;")
                #self.tableview.setSelectionBehavior(QTableView.SelectRows);
                item_0.setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
            else:
                item_0.setForeground(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            
            item_1 = self.tableBids.cellWidget(i, 1)
            item_1.setRange(0, 100)
            item_1.setFormat(f"{round(data[i]['bs'],3):,}")

            self.asksAnim[i].setStartValue(data[9-i]['as']/asks_size)
            self.asksAnim[i].setEndValue(data[9-i]['as']/asks_size)
            self.asksAnim[i].start()
            self.bidsAnim[i].setStartValue(data[i]['bs']/bids_size)
            self.bidsAnim[i].setEndValue(data[i]['bs']/bids_size)
            self.bidsAnim[i].start()
       
    def closeEvent(self, event):
        self.ow.close()


if __name__ == "__main__":
    import sys

    import aiopyupbit
    import config
    import utils

#   위에 3개 지움


    # NOTE Windows 운영체제 환경에서 Python 3.7+부터 발생하는 EventLoop RuntimeError 관련 처리
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
	    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


#요기부터
    utils.set_windows_selector_event_loop_global()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=config.FIAT, contain_name=True))

#요기까지 지움


    static.chart = component.RealtimeManager(codes=codes)
    static.chart.start()

    app = QApplication(sys.argv)
    ow = OrderbookWidget()
    ow.show()

    #cw = test_chart_list.ChartlistWidget()
    #cw.show()
    exit(app.exec_())
