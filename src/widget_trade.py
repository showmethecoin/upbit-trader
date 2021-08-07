# !/usr/bin/python
# -*- coding: utf-8 -*-
import math
import asyncio as aio
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
import ui_styles
import static
from utils import get_file_path
from static import log

class TradeWorker(QThread):
    dataSent = pyqtSignal(object, int)
    def __init__(self, code):
        super().__init__()
        self.alive = False
        self.code = code
    
    def run(self):
        self.alive = True
        while self.alive:
            time.sleep(0.5)
            wait = aio.run(static.account.upbit.get_order(ticker_or_uuid= self.code))
            done = aio.run(static.account.upbit.get_order(ticker_or_uuid= self.code, state = 'done'))
            self.dataSent.emit(wait, 1)
            self.dataSent.emit(done, 2)
    
    def close(self) -> None:
        self.alive = False
        return super().terminate()

class TradeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(get_file_path("styles/ui/trade.ui"), self)

        self.coin = 'KRW-BTC'
        self.items1 = []
        self.items2 = []
        self.info_table_1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.info_table_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tw = TradeWorker(self.coin)
        self.tw.dataSent.connect(self.set_execute_info)
        
        ''' Bid '''
        # Bid Radio Clicked Listener Initialize
        self.buy_designation_price.setChecked(True)
        self.info_not_execution.setChecked(True)
        self.buy_designation_price.clicked.connect(
            self.clicked_buy_designation_price)
        self.buy_market_price.clicked.connect(self.clicked_buy_market_pice)
        self.buy_reservation_price.clicked.connect(
            self.clicked_buy_reservation_pice)

        # Bid Reset-Button Clicked Listener Initialize
        self.buy_reset_1.clicked.connect(self.clicked_reset)
        self.buy_reset_2.clicked.connect(self.clicked_reset)
        self.buy_reset_3.clicked.connect(self.clicked_reset)

        # Bid percent Clicked Listener Initialize
        self.buy_ten_1.clicked.connect(lambda: self.clicked_vol(0.1))
        self.buy_twenty_fifth_1.clicked.connect(lambda: self.clicked_vol(0.25))
        self.buy_fifty_1.clicked.connect(lambda: self.clicked_vol(0.5))
        self.buy_hundred_1.clicked.connect(lambda: self.clicked_vol(1))
        self.buy_ten_2.clicked.connect(lambda: self.clicked_vol(0.1))
        self.buy_twenty_fifth_2.clicked.connect(lambda: self.clicked_vol(0.25))
        self.buy_fifty_2.clicked.connect(lambda: self.clicked_vol(0.5))
        self.buy_hundred_2.clicked.connect(lambda: self.clicked_vol(1))
        self.buy_ten_3.clicked.connect(lambda: self.clicked_vol(0.1))
        self.buy_twenty_fifth_3.clicked.connect(lambda: self.clicked_vol(0.25))
        self.buy_fifty_3.clicked.connect(lambda: self.clicked_vol(0.5))
        self.buy_hundred_3.clicked.connect(lambda: self.clicked_vol(1))
        
        # Bid Button Clicked Listener Initialize
        self.buy_buy_btn_1.clicked.connect(lambda: self.clicked_buy_button(1))
        self.buy_buy_btn_2.clicked.connect(lambda: self.clicked_buy_button(2))
        self.buy_buy_btn_3.clicked.connect(lambda: self.clicked_buy_button(3))
        
        # Bid Price Changed Listener Initialize
        self.buy_price_1.setGroupSeparatorShown(True)
        self.buy_price_1.textChanged.connect(self.changed_price)
        self.buy_volume_1.textChanged.connect(self.changed_volume)
        self.buy_total_price_1.textChanged.connect(self.changed_total)
        self.buy_price_3.textChanged.connect(self.changed_price)
        self.buy_volume_3.textChanged.connect(self.changed_volume)
        self.buy_total_price_3.textChanged.connect(self.changed_total)
        
        ''' Ask '''
        # Ask Radio Clicked Listener Initialize
        self.sell_designation_price.setChecked(True)
        self.sell_designation_price.clicked.connect(
            self.clicked_sell_designation_price)
        self.sell_market_price.clicked.connect(
            self.clicked_sell_market_pice)
        self.sell_reservation_price.clicked.connect(
            self.clicked_sell_reservation_pice)

        # Ask Reset-Button Clicked Listener Initialize
        self.sell_reset_1.clicked.connect(self.clicked_reset)
        self.sell_reset_2.clicked.connect(self.clicked_reset)
        self.sell_reset_3.clicked.connect(self.clicked_reset)

        # Ask percent Clicked Listener Initialize
        self.sell_ten_1.clicked.connect(lambda: self.clicked_vol(0.1))
        self.sell_twenty_fifth_1.clicked.connect(lambda: self.clicked_vol(0.25))
        self.sell_fifty_1.clicked.connect(lambda: self.clicked_vol(0.5))
        self.sell_hundred_1.clicked.connect(lambda: self.clicked_vol(1))
        self.sell_ten_2.clicked.connect(lambda: self.clicked_vol(0.1))
        self.sell_twenty_fifth_2.clicked.connect(lambda: self.clicked_vol(0.25))
        self.sell_fifty_2.clicked.connect(lambda: self.clicked_vol(0.5))
        self.sell_hundred_2.clicked.connect(lambda: self.clicked_vol(1))
        self.sell_ten_3.clicked.connect(lambda: self.clicked_vol(0.1))
        self.sell_twenty_fifth_3.clicked.connect(lambda: self.clicked_vol(0.25))
        self.sell_fifty_3.clicked.connect(lambda: self.clicked_vol(0.5))
        self.sell_hundred_3.clicked.connect(lambda: self.clicked_vol(1))

        # Ask Button Clicked Listener Initialize
        self.sell_sell_btn_1.clicked.connect(
            lambda: self.clicked_sell_button(1))
        self.sell_sell_btn_2.clicked.connect(
            lambda: self.clicked_sell_button(2))
        self.sell_sell_btn_3.clicked.connect(
            lambda: self.clicked_sell_button(3))

        # Ask Price Changed Listener Initialize
        self.sell_price_1.textChanged.connect(self.changed_price)
        self.sell_volume_1.textChanged.connect(self.changed_volume)
        self.sell_total_price_1.textChanged.connect(self.changed_total)
        self.sell_price_3.textChanged.connect(self.changed_price)
        self.sell_volume_3.textChanged.connect(self.changed_volume)
        self.sell_total_price_3.textChanged.connect(self.changed_total)
        
        # Volume changed signal
        self.volume_changed = True

        # INFO Radio Button Clicked Listener Initialize
        self.info_not_execution.clicked.connect(lambda: self.clicked_info_radio(0))
        self.info_execution.clicked.connect(lambda: self.clicked_info_radio(1))

        self.cancel_button.clicked.connect(self.clicked_cancel)

    # Clicked Event Function
    def clicked_buy_designation_price(self):
        self.buy_stack.setCurrentIndex(0)

    def clicked_buy_market_pice(self):
        self.buy_stack.setCurrentIndex(1)

    def clicked_buy_reservation_pice(self):
        self.buy_stack.setCurrentIndex(2)

    def clicked_sell_designation_price(self):
        self.sell_stack.setCurrentIndex(0)

    def clicked_sell_market_pice(self):
        self.sell_stack.setCurrentIndex(1)

    def clicked_sell_reservation_pice(self):
        self.sell_stack.setCurrentIndex(2)

    def clicked_vol(self, ratio):   
        cash = static.account.get_total_cash()
        # Bid
        if self.tabWidget.currentIndex() == 0:
            total_order_price = cash * ratio
            total_order_price -= math.ceil(total_order_price * static.FEES)
            idx = self.buy_stack.currentIndex()
            if idx == 0:
                self.buy_total_price_1.setValue(total_order_price)
            elif idx == 1:
                self.buy_total_price_2.setValue(total_order_price)
            else:
                self.buy_total_price_3.setValue(total_order_price)
        # Ask
        else:
            self.volume_changed = False
            coin = self.sell_ticker_1.text()
            if coin in static.account.coins.keys():
                price = self.sell_price_1.value()
                balance = static.account.coins[coin]['balance']
                idx = self.sell_stack.currentIndex()
                volume = balance * ratio
                if idx == 0:
                    # TODO 여기다 시팔
                    self.sell_total_price_1.setValue(price * volume)
                    self.sell_volume_1.setValue(volume)
                elif idx == 1:
                    # TODO 텍스트를 주문 총액에서 수량으로 변경 필요
                    self.sell_total_price_2.setValue(volume)
                else:
                    self.sell_total_price_3.setValue(price * volume) 
                    self.sell_volume_1.setValue(volume)           

    def clicked_reset(self):
        # Bid
        if self.tabWidget.currentIndex() == 0:
            idx = self.buy_stack.currentIndex()
            if idx == 0:
                self.buy_price_1.setValue(0)
                self.buy_volume_1.setValue(0)
                self.buy_total_price_1.setValue(0)
            elif idx == 1:
                self.buy_total_price_2.setValue(0)
            else:
                self.buy_price_3.setValue(0)
                self.buy_volume_3.setValue(0)
                self.buy_total_price_3.setValue(0)
                self.buy_monitor_price_3.setValue(0)
        # Ask
        else:
            idx = self.sell_stack.currentIndex()
            if idx == 0:
                self.sell_price_1.setValue(0)
                self.sell_volume_1.setValue(0)
                self.sell_total_price_1.setValue(0)
            elif idx == 1:
                self.sell_total_price_2.setValue(0)
            else:
                self.sell_price_3.setValue(0)
                self.sell_volume_3.setValue(0)
                self.sell_total_price_3.setValue(0)
                self.sell_monitor_price_3.setValue(0)

    def clicked_buy_button(self, tab_number):
        try:
            ticker = self.coin
            # Limit order
            if tab_number == 1:
                buy_price = self.buy_price_1.value()
                buy_volume = self.buy_volume_1.value()
                total_buy_price = self.buy_total_price_1.value()
                ret = aio.run(static.account.upbit.buy_limit_order(ticker=ticker,
                                                                       price=buy_price,
                                                                       volume=buy_volume))
            # Market order
            elif tab_number == 2:
                total_buy_price = self.buy_total_price_2.value()
                ret = aio.run(static.account.upbit.buy_market_order(ticker=ticker,
                                                                        price=total_buy_price))
            # TODO Reservation order
            else:
                self.show_messagebox(False, '미구현입니다')
                return
                # buy_price = self.buy_price_3.value()
                # monitoring_price = self.buy_monitor_price_3.value()
                # buy_volume = self.buy_volume_3.value()
                # total_buy_price = self.buy_total_price_3.value()
            log.info(f'{ret}')
            self.show_messagebox(True, '매수주문이 정상완료되었습니다.')
        except Exception as e:
            self.show_messagebox(False, e.__str__())

    def clicked_sell_button(self, tab_number):
        try:
            ticker = self.coin
            # Limit order
            if tab_number == 1:
                sell_price = self.sell_price_1.value()
                sell_volume = self.sell_volume_1.value()
                log.info(f'{sell_price} {sell_volume}')
                ret = aio.run(static.account.upbit.sell_limit_order(ticker=ticker,
                                                                        price=sell_price,
                                                                        volume=sell_volume))
            # Market order
            elif tab_number == 2:
                sell_volume = self.sell_total_price_2.value()
                # TODO 개수 바꿔야함
                ret = aio.run(static.account.upbit.sell_market_order(ticker=ticker,
                                                                     volume=sell_volume))
            # TODO Reservation order
            else:
                self.show_messagebox(False, '미구현입니다')
                return
                # sell_price = self.sell_price_3.value()
                # monitoring_price = self.sell_monitor_price_3.value()
                # total_sell_price = self.sell_total_price_3.value()
            log.info(f'{ret}')
            self.show_messagebox(True, '매도주문이 정상완료되었습니다.')
        except Exception as e:
            self.show_messagebox(False, e)
    
    def clicked_info_radio(self, index):
        self.info_stack.setCurrentIndex(index)
    
    def clicked_cancel(self):
        table = self.info_table_1
        idx = table.currentIndex().row()
        ticker = self.tw.code

        # 선택한 row가 없는 경우
        if idx == -1:
            return
        
        # 선택된 row의 datetime 저장
        dtime = table.item(idx, 0).text()
        wait = aio.run(static.account.upbit.get_order(ticker_or_uuid= ticker))

        for data in wait:
            date = data['created_at'].split('T')[0]
            time = data['created_at'].split('T')[1].split('+')[0]
            date_time = date +"\n" + time

            # 미체결 내역중 datetime이 일치하는 내역을 찾은 경우
            if(date_time == dtime):
                aio.run(static.account.upbit.cancel_order(uuid= data['uuid']))
        
    def show_messagebox(self, condition, message):
        self.msg = QMessageBox()
        if condition:
            self.msg.setIcon(QMessageBox.Information)
        else:
            self.msg.setIcon(QMessageBox.Critical)
        self.msg.autoFillBackground()
        # self.msg.setWindowTitle('Authentication error')
        self.msg.setText(f'{message}')
        self.msg.show()

    # Change Event Function
    def changed_price(self):
        self.set_total_price()

    def changed_volume(self):
        self.set_total_price()

    def changed_total(self):
        if self.volume_changed:
            # Bid
            if self.tabWidget.currentIndex() == 0:
                idx = self.buy_stack.currentIndex()
                if idx == 0 and self.buy_price_1.value() != 0.0:
                    total_order_price = self.buy_total_price_1.value()
                    target_price = self.buy_price_1.value()
                    volume = round(total_order_price / target_price, 8)
                    self.buy_volume_1.setValue(volume)
                elif self.buy_price_3.value() != 0.0:
                    total_order_price = self.buy_total_price_3.value()
                    target_price = self.buy_price_3.value()
                    volume = round(total_order_price / target_price, 8)
                    self.buy_volume_3.setValue(volume)
            # Ask
            else:
                idx = self.sell_stack.currentIndex()
                if idx == 0 and self.sell_price_1.value() != 0.0:
                    total_order_price = self.sell_total_price_1.value()
                    target_price = self.sell_price_1.value()
                    volume = round(total_order_price / target_price, 8)
                    self.sell_volume_1.setValue(volume)
                elif self.sell_price_3.value() != 0.0:
                    total_order_price = self.sell_total_price_3.value()
                    target_price = self.sell_price_3.value()
                    volume = round(total_order_price / target_price, 8)
                    self.sell_volume_3.setValue(volume)
        else:
            self.volume_changed = True

    def set_execute_info(self, data, idx):
        table = self.info_table_1
        items = self.items1

        if idx == 2:
            table = self.info_table_2
            items = self.items2
            self.set_own_asset(self.tw.code.split('-')[1])

        if table.rowCount() != len(data):
            table.clearContents() # 테이블 지우고
            table.setRowCount(0)
            items.clear()
            
            # 찍을 데이터가 없는 경우
            if len(data) == 0:
                return
            
            # 동적으로 row관리
            count_data = len(data)
            table.setRowCount(count_data)
            font = QFont()
            font.setBold(True)

            for i in range(count_data):
                items.append([QTableWidgetItem(), QTableWidgetItem(), QTableWidgetItem(), QTableWidgetItem()])
                items[i][0].setFont(font)
                items[i][0].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                items[i][1].setFont(font)
                items[i][1].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                items[i][2].setFont(font)
                items[i][2].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                items[i][3].setFont(font)
                items[i][3].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

                table.setItem(i, 0, items[i][0])       
                table.setItem(i, 1, items[i][1])
                table.setItem(i, 2, items[i][2])       
                table.setItem(i, 3, items[i][3])
            table.verticalHeader().setDefaultSectionSize(60)
        
        for i, info in enumerate(data):
            # 테이블 개수와 맞지 않으면 업데이트x
            if len(data) != len(items):
                break
            
            # DATE TIME
            date = info['created_at'].split('T')[0]
            time = info['created_at'].split('T')[1].split('+')[0]
            items[i][0].setText(date +"\n" + time)

            # MARKET AND SIDE
            if info['side'] == 'bid':
                items[i][1].setText(info['market']+"\n매수")
            elif info['side'] == 'ask':
                items[i][1].setText(info['market'] + "\n매도")
            
            # PRICE AND KRW
            if info['price'] != None:
                krw = int(float(info['price']) * float(info['volume']))
                items[i][2].setText(f'{info["price"]}\n{krw}')
            else:
                items[i][2].setText(info['price'])
            
            # VOLUME
            items[i][3].setText(info['volume'])
    
    # Calc Latest Total-Price
    def set_total_price(self):
        # Bid
        if self.tabWidget.currentIndex() == 0:
            idx = self.buy_stack.currentIndex()
            if idx == 0:
                target_price = self.buy_price_1.value()
                volume = self.buy_volume_1.value()
                total_order_price = target_price * volume
                self.buy_total_price_1.setValue(total_order_price)
            else:
                target_price = self.buy_price_3.value()
                volume = self.buy_volume_3.value()
                total_order_price = target_price * volume
                self.buy_total_price_3.setValue(total_order_price)
        # Ask
        else:
            idx = self.sell_stack.currentIndex()
            if idx == 0:
                target_price = self.sell_price_1.value()
                volume = self.sell_volume_1.value()
                total_order_price = target_price * volume
                self.sell_total_price_1.setValue(total_order_price)
            else:
                target_price = self.sell_price_3.value()
                volume = self.sell_volume_3.value()
                total_order_price = target_price * volume
                self.sell_total_price_3.setValue(total_order_price)

    # All page Reset
    def all_reset(self):
        self.buy_price_1.setValue(0.0)
        self.buy_volume_1.setValue(0.0)
        self.buy_total_price_1.setValue(0.0)
        self.buy_total_price_2.setValue(0.0)
        self.buy_price_3.setValue(0.0)
        self.buy_volume_3.setValue(0.0)
        self.buy_total_price_3.setValue(0.0)
        self.buy_monitor_price_3.setValue(0.0)
        self.sell_price_1.setValue(0.0)
        self.sell_volume_1.setValue(0.0)
        self.sell_total_price_1.setValue(0.0)
        self.sell_total_price_2.setValue(0.0)
        self.sell_price_3.setValue(0.0)
        self.sell_volume_3.setValue(0.0)
        self.sell_total_price_3.setValue(0.0)
        self.sell_monitor_price_3.setValue(0.0)

    # Set Price
    def set_price(self, ticker):

        # refresh price
        self.all_reset()

        # Set coin code
        self.coin = ticker

        # worker thread update
        self.tw.code = ticker
        self.info_table_1.clearContents()
        self.info_table_1.setRowCount(0)
        self.info_table_2.clearContents()
        self.info_table_2.setRowCount(0)
        self.items1.clear()
        self.items2.clear()

        coin = ticker.split("-")[1]
        self.sell_ticker_1.setText(coin)
        self.sell_ticker_2.setText(coin)
        self.sell_ticker_3.setText(coin)

        self.set_own_asset(coin)
        # Set trade price
        market_price = static.chart.coins[ticker].get_trade_price()
        self.buy_price_1.setValue(market_price)
        self.buy_price_3.setValue(market_price)
        self.sell_price_1.setValue(market_price)
        self.sell_price_3.setValue(market_price)
    
    def set_own_asset(self, coin):
        # Bid: Set own cash
        cash = str(int(static.account.cash))
        self.buy_orderable_1.setText(cash)
        self.buy_orderable_2.setText(cash)
        self.buy_orderable_3.setText(cash)

        # Ask: Set own coin
        if coin in static.account.coins.keys():
            balance = f'{static.account.coins[coin]["balance"]:,.8f}'
            self.sell_orderable_1.setText(balance)
            self.sell_orderable_2.setText(balance)
            self.sell_orderable_3.setText(balance)
        else:
            self.sell_orderable_1.setText("0.0")
            self.sell_orderable_2.setText("0.0")
            self.sell_orderable_3.setText("0.0")
    
    def set_current_price(self, cur_price):
        self.volume_changed = False
        self.buy_price_1.setValue(cur_price)
        self.buy_price_3.setValue(cur_price)
        self.sell_price_1.setValue(cur_price)
        self.sell_price_3.setValue(cur_price)
    
    def closeEvent(self, event):
        self.tw.close()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = TradeWidget()
    window.show()
    sys.exit(app.exec_())
