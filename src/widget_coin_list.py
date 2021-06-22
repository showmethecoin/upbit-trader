# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import asyncio as aio
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QWidget, QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils import get_file_path
import static


class CoinListWorker(QThread):
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
        uic.loadUi(get_file_path("styles/ui/coin_list.ui"), self)

        #화면 수직,수평으로 늘릴 경우 칸에 맞게 변경됨
        #사용 가능한 공간을 채우기 위해 섹션의 크기를 자동으로 조정
        #참고 QHeaderView Class
        self.coin_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.coin_list.horizontalHeader().sectionClicked.connect(self.chkTopClicked)
        # self.coin_list.horizontalHeader(0).setToolTip()
        # self.coin_list.setSortingEnabled(True)
        self.coin_list.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.cw = CoinListWorker()
        self.cw.dataSent.connect(self.updateData)

        self.coin_list.cellClicked.connect(self.chkItemClicked)
        self.order = None
        self.chart = None

        self.color_red = QBrush(QColor(207, 48, 74))  # CF304A
        self.color_green = QBrush(QColor(2, 192, 118))  # 02C076
        self.color_white = QBrush(QColor(255, 255, 255))

    def updateData(self, data):
        # 테이블 설정
        # 테이블을 처음 설정할 경우 또는 설정된 table row갯수와 set해야되는 data갯수가 다를 경우
        if self.coin_list.rowCount() == 0 or self.coin_list.rowCount() != len(static.chart.codes):
            self.coin_list.clearContents() # 테이블 지우고
            self.items = []
            # 동적으로 row관리
            count_codes = len(static.chart.codes)
            self.coin_list.setRowCount(count_codes)
            font = QFont()
            font.setBold(True)

            for i in range(count_codes):
                self.items.append([QTableWidgetItem(), QTableWidgetItem(), QTableWidgetItem()])
                self.items[i][0].setFont(font)
                self.items[i][0].setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.items[i][1].setFont(font)
                self.items[i][1].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.items[i][2].setFont(font)
                self.items[i][2].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)  
                self.coin_list.setItem(i, 0, self.items[i][0])       
                self.coin_list.setItem(i, 1, self.items[i][1])
                self.coin_list.setItem(i, 2, self.items[i][2])

        for i, coin in enumerate(data):
            change_rate = coin.get_signed_change_rate()
            self.items[i][0].setText(f'{coin.korean_name}({coin.code[4:]})')
            self.items[i][1].setText(f'{(lambda x: x if x < 100 else int(x))(coin.get_trade_price()):,}')
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
                
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.dw.close()
        return super().closeEvent(a0)

    def setOrder(self, order):
        self.order = order

    def setChart(self, chart):
        self.chart = chart

    def setTrade(self, trade):
        self.trade = trade

    def chkItemClicked(self):
        select_item = self.coin_list.selectedItems()
        if len(select_item) == 0:
            return
        code = f"KRW-{select_item[0].text().split('(')[1][:-1]}"
        self.order.ow.ticker = code
        self.chart.set_coin(code)
        self.trade.set_price(code)

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
    from component import RealtimeManager
    from utils import set_windows_selector_event_loop_global
    
    set_windows_selector_event_loop_global()

    # Upbit coin chart
    loop = aio.new_event_loop()
    aio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=static.FIAT, contain_name=True))
    static.chart = RealtimeManager(codes=codes)
    static.chart.start()

    app = QApplication(sys.argv)
    cw = CoinlistWidget()
    cw.show()
    exit(app.exec_())
