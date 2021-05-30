# !/usr/bin/python
# -*- coding: utf-8 -*-
import math
import asyncio
from PyQt5.QtWidgets import *
from PyQt5 import uic
import ui_styles
import static
import utils

class TradeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(utils.get_file_path("styles/ui/trade.ui"), self)
        
        self.coin = 'KRW-BTC'
        # BUY Radio Clicked Listener Initialize
        self.buy_designation_price.setChecked(True)
        self.buy_designation_price.clicked.connect(
            self.clicked_buy_designation_price)
        self.buy_market_price.clicked.connect(self.clicked_buy_market_pice)
        self.buy_reservation_price.clicked.connect(
            self.clicked_buy_reservation_pice)

        # SELL Radio Clicked Listener Initialize
        self.sell_designation_price.setChecked(True)
        self.sell_designation_price.clicked.connect(
            self.clicked_sell_designation_price)
        self.sell_market_price.clicked.connect(
            self.clicked_sell_market_pice)
        self.sell_reservation_price.clicked.connect(
            self.clicked_sell_reservation_pice)

        # BUY Reset-Button Clicked Listener Initialize
        self.buy_reset_1.clicked.connect(self.clicked_reset)
        self.buy_reset_2.clicked.connect(self.clicked_reset)
        self.buy_reset_3.clicked.connect(self.clicked_reset)

        # BUY percent Cliked Listenr Initialize
        self.buy_ten_1.clicked.connect(lambda: self.clicked_vol(10))
        self.buy_twenty_fifth_1.clicked.connect(lambda: self.clicked_vol(25))
        self.buy_fifty_1.clicked.connect(lambda: self.clicked_vol(50))
        self.buy_hundred_1.clicked.connect(lambda: self.clicked_vol(100))

        self.buy_ten_2.clicked.connect(lambda: self.clicked_vol(10))
        self.buy_twenty_fifth_2.clicked.connect(lambda: self.clicked_vol(25))
        self.buy_fifty_2.clicked.connect(lambda: self.clicked_vol(50))
        self.buy_hundred_2.clicked.connect(lambda: self.clicked_vol(100))
        
        self.buy_ten_3.clicked.connect(lambda: self.clicked_vol(10))
        self.buy_twenty_fifth_3.clicked.connect(lambda: self.clicked_vol(25))
        self.buy_fifty_3.clicked.connect(lambda: self.clicked_vol(50))
        self.buy_hundred_3.clicked.connect(lambda: self.clicked_vol(100))

        # SELL Reset-Button Clicked Listener Initialize
        self.sell_reset_1.clicked.connect(self.clicked_reset)
        self.sell_reset_2.clicked.connect(self.clicked_reset)
        self.sell_reset_3.clicked.connect(self.clicked_reset)

        # SELL percent Cliked Listenr Initialize
        self.sell_ten_1.clicked.connect(lambda: self.clicked_vol(10))
        self.sell_twenty_fifth_1.clicked.connect(lambda: self.clicked_vol(25))
        self.sell_fifty_1.clicked.connect(lambda: self.clicked_vol(50))
        self.sell_hundred_1.clicked.connect(lambda: self.clicked_vol(100))
        
        self.sell_ten_2.clicked.connect(lambda: self.clicked_vol(10))
        self.sell_twenty_fifth_2.clicked.connect(lambda: self.clicked_vol(25))
        self.sell_fifty_2.clicked.connect(lambda: self.clicked_vol(50))
        self.sell_hundred_2.clicked.connect(lambda: self.clicked_vol(100))

        self.sell_ten_3.clicked.connect(lambda: self.clicked_vol(10))
        self.sell_twenty_fifth_3.clicked.connect(lambda: self.clicked_vol(25))
        self.sell_fifty_3.clicked.connect(lambda: self.clicked_vol(50))
        self.sell_hundred_3.clicked.connect(lambda: self.clicked_vol(100))

        # BUY Button Clicked Listenr Initialize
        self.buy_buy_btn_1.clicked.connect(lambda: self.clicked_buy_button(1))
        self.buy_buy_btn_2.clicked.connect(lambda: self.clicked_buy_button(2))
        self.buy_buy_btn_3.clicked.connect(lambda: self.clicked_buy_button(3))

        # SELL Button Clicked Listenr Initialize
        self.sell_sell_btn_1.clicked.connect(lambda: self.clicked_sell_button(1))
        self.sell_sell_btn_2.clicked.connect(lambda: self.clicked_sell_button(2))
        self.sell_sell_btn_3.clicked.connect(lambda: self.clicked_sell_button(3))

        # BUY Price Changed Listener Initialize
        self.buy_price_1.setGroupSeparatorShown(True)
        self.buy_price_1.textChanged.connect(self.changed_price)
        self.buy_volume_1.textChanged.connect(self.changed_volume)
        self.buy_total_price_1.textChanged.connect(self.changed_total)
        self.buy_price_3.textChanged.connect(self.changed_price)
        self.buy_volume_3.textChanged.connect(self.changed_volume)
        self.buy_total_price_3.textChanged.connect(self.changed_total)

        # SELL Price Changed Listener Initialize
        self.sell_price_1.textChanged.connect(self.changed_price)
        self.sell_volume_1.textChanged.connect(self.changed_volume)
        self.sell_total_price_1.textChanged.connect(self.changed_total)
        self.sell_price_3.textChanged.connect(self.changed_price)
        self.sell_volume_3.textChanged.connect(self.changed_volume)
        self.sell_total_price_3.textChanged.connect(self.changed_total)

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
    
    def clicked_vol(self, num):
        # TODO 라운딩 방식 개선 필요
        percent = num / 100.0
        cash = static.account.cash + static.account.locked_cash

        # BUY
        if self.tabWidget.currentIndex() == 0:
            idx = self.buy_stack.currentIndex()
            # Designation
            if idx == 0:
                self.buy_total_price_1.setValue(cash * percent)
            # Market
            elif idx == 1:
                self.buy_total_price_2.setValue(cash * percent)
            # Reservation
            else:
                self.buy_total_price_3.setValue(cash * percent)
        # SELL
        else:
            idx = self.sell_stack.currentIndex()
            coin = self.sell_ticker_1.text()
            price = self.sell_price_1.value()
            balance = 0.0
            if coin in static.account.coins.keys():
                balance = static.account.coins[coin]['balance']

            # Designation
            if idx == 0:
                self.sell_total_price_1.setValue(price * balance * percent)
            # Market
            elif idx == 1:
                # TODO 텍스트를 주문 총액에서 수량으로 변경 필요
                self.sell_total_price_2.setValue(balance * percent)
            # Reservation
            else:
                self.sell_total_price_3.setValue(price * balance * percent)
    
    def clicked_reset(self):
        # BUY
        if self.tabWidget.currentIndex() == 0:
            idx = self.buy_stack.currentIndex()

            # Designation
            if idx == 0:
                self.buy_price_1.setValue(0.0)
                self.buy_volume_1.setValue(0.0)
                self.buy_total_price_1.setValue(0.0)
            # Market
            elif idx == 1:
                self.buy_total_price_2.setValue(0.0)
            # Reservation
            else:
                self.buy_price_3.setValue(0.0)
                self.buy_volume_3.setValue(0.0)
                self.buy_total_price_3.setValue(0.0)
                self.buy_monitor_price_3.setValue(0.0)
        # SELL
        else:
            idx = self.sell_stack.currentIndex()

            # Designation
            if idx == 0:
                self.sell_price_1.setValue(0.0)
                self.sell_volume_1.setValue(0.0)
                self.sell_total_price_1.setValue(0.0)
            # Market
            elif idx == 1:
                self.sell_total_price_2.setValue(0.0)
            # Reservation
            else:
                self.sell_price_3.setValue(0.0)
                self.sell_volume_3.setValue(0.0)
                self.sell_total_price_3.setValue(0.0)
                self.sell_monitor_price_3.setValue(0.0)

    def clicked_buy_button(self, tab_number):
        cash = static.account.cash
        ticker = self.coin   
        # 지정가 매수
        if tab_number == 1:
            buy_price = self.buy_price_1.value()
            buy_volume = self.buy_volume_1.value()
            total_buy_price = self.buy_total_price_1.value()
            if total_buy_price <= static.MIN_TRADE_PRICE:
                self.show_messagebox(False, '주문 최소금액은 5000 KRW 입니다.')
                return
            elif total_buy_price + math.ceil(total_buy_price * static.FEES) > cash:
                self.show_messagebox(False, '금액이 부족합니다.')
                return
            ret = asyncio.run(static.account.upbit.buy_limit_order(ticker=ticker, 
                                                                   price=buy_price, 
                                                                   volume=buy_volume))
        # 시장가 매수
        elif tab_number == 2 :
            total_buy_price = self.buy_total_price_2.value()
            if total_buy_price <= static.MIN_TRADE_PRICE:
                self.show_messagebox(False, '주문 최소금액은 5000 KRW 입니다.')
                return
            if total_buy_price + math.ceil(total_buy_price * static.FEES) > cash :
                self.show_messagebox(False, '금액이 부족합니다.')
                return
            ret = asyncio.run(static.account.upbit.buy_market_order(ticker=ticker, 
                                                                    price=total_buy_price))
        # 예약-지정가 매수
        # TODO 미구현
        else:
            self.show_messagebox(False, '미구현입니다')
            return
            # buy_price = self.buy_price_3.value()
            # monitoring_price = self.buy_monitor_price_3.value()
            # buy_volume = self.buy_volume_3.value()
            # total_buy_price = self.buy_total_price_3.value()
            # if total_buy_price <= static.MIN_TRADE_PRICE:
            #     self.show_messagebox('주문 최소금액은 5000 KRW 입니다.')
            #     return
            # if total_buy_price + math.upper(total_buy_price * static.FEES) > cash :
            #     self.show_messagebox('금액이 부족합니다.')
            #     return
                
        print(ret)
        self.show_messagebox(True, '매수주문이 정상완료되었습니다.')
    
    def clicked_sell_button(self, tab_number):
        coin = self.coin.split('-')[1]
        if coin not in static.account.coins.keys():
            self.show_messagebox(False, '보유한 코인이 없습니다.')
            return
        balance = static.account.coins[coin]['balance']
        ticker = self.coin
        # 지정가 매도
        if tab_number == 1:
            sell_price = self.sell_price_1.value()
            sell_volume = self.sell_volume_1.value()
            total_sell_price = self.sell_total_price_1.value()
            if total_sell_price <= static.MIN_TRADE_PRICE:
                self.show_messagebox(False, '주문 최소금액은 5000 KRW 입니다.')
                return
            elif self.sell_price_1.value() != 0.0 and (total_sell_price / sell_price) > balance :
                self.show_messagebox(False, '금액이 부족합니다.')
                return 
            ret = asyncio.run(static.account.upbit.sell_limit_order(ticker=ticker, 
                                                                    price=sell_price, 
                                                                    volume=sell_volume))
        # 시장가 매도
        elif tab_number == 2 :
            sell_volume = self.sell_total_price_2.value()
            if sell_volume * static.chart.get_coin(ticker).get_trade_price() <= static.MIN_TRADE_PRICE:
                self.show_messagebox(False, '주문 최소금액은 5000 KRW 입니다.')
                return
            # TODO 개수 바꿔야함
            ret = asyncio.run(static.account.upbit.sell_market_order(ticker=ticker, 
                                                                     volume=sell_volume))
            
        # 예약 지정가 매도
        # TODO 미구현
        else:
            self.show_messagebox(False, '미구현입니다')
            return
            # if self.sell_total_price_3.value() < static.MIN_TRADE_PRICE:
            #     self.show_messagebox('주문 최소금액은 5000 KRW 입니다.')
            #     return
            # if self.sell_price_3.value() != 0.0 and (self.sell_total_price_3.value() / self.sell_price_3.value()) > balance :
            #     self.show_messagebox('금액이 부족합니다.')
            #     return
            # print('Ticker : ', self.coin)
            # print('Sell Price : ', self.sell_price_3.value())
            # print('Monitoring Price : ', self.sell_monitor_price_3.value())
            # print('Total KRW : ', self.sell_total_price_3.value())
        print(ret)
        self.show_messagebox(True, '매도주문이 정상완료되었습니다.')
        
    def show_messagebox(self, condition, message):
        self.msg = QMessageBox()
        if condition:
            self.msg.setIcon(QMessageBox.Information)
        else:
            self.msg.setIcon(QMessageBox.Critical)
        self.msg.autoFillBackground()
        self.msg.setWindowTitle('Authentication error')
        self.msg.setText(f'{message}')
        self.msg.show()

    # Change Event Function
    def changed_price(self):
        self.set_total_price()

    def changed_volume(self):
        self.set_total_price()

    def changed_total(self):
        # BUY
        if self.tabWidget.currentIndex() == 0:
            idx = self.buy_stack.currentIndex()

            # Designation
            if idx == 0 and self.buy_price_1.value() != 0.0:
                self.buy_volume_1.setValue(
                    round(self.buy_total_price_1.value() / self.buy_price_1.value(), 8))
            # Reservation
            elif self.buy_price_3.value() != 0.0:
                self.buy_volume_3.setValue(
                    round(self.buy_total_price_3.value() / self.buy_price_3.value(), 8))

        # SELL
        else:
            idx = self.sell_stack.currentIndex()

            # Designation
            if idx == 0 and self.sell_price_1.value() != 0.0:
                self.sell_volume_1.setValue(
                    round(self.sell_total_price_1.value() / self.sell_price_1.value(), 8))
            # Reservation
            elif self.sell_price_3.value() != 0.0:
                self.sell_volume_3.setValue(
                    round(self.sell_total_price_3.value() / self.sell_price_3.value(), 8))

    # Calc Latest Total-Price
    def set_total_price(self):
        # BUY
        if self.tabWidget.currentIndex() == 0:
            idx = self.buy_stack.currentIndex()
            # Designation
            if idx == 0:
                self.buy_total_price_1.setValue(
                    round(self.buy_price_1.value() * self.buy_volume_1.value()))
            # Reservation
            else:
                self.buy_total_price_3.setValue(
                    round(self.buy_price_3.value() * self.buy_volume_3.value()))

        # SELL
        else:
            idx = self.sell_stack.currentIndex()

            # Designation
            if idx == 0:
                self.sell_total_price_1.setValue(
                    round(self.sell_price_1.value() * self.sell_volume_1.value()))
            # Reservation
            else:
                self.sell_total_price_3.setValue(
                    round(self.sell_price_3.value() * self.sell_volume_3.value()))

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
        if static.chart == None:
            return
        # set market price 
        market_price = static.chart.coins[ticker].get_trade_price()
        
        # set held cash
        cash = str(static.account.cash + static.account.locked_cash)
        self.buy_orderable_1.setText(cash)
        self.buy_orderable_2.setText(cash)
        self.buy_orderable_3.setText(cash)

        # set coin name
        self.coin = ticker
        coin = ticker.split("-")[1]
        self.sell_ticker_1.setText(coin)
        self.sell_ticker_2.setText(coin)
        self.sell_ticker_3.setText(coin)

        balance = "0.0"
        
        # set held coin 
        if coin in static.account.coins.keys():
            coin_val = static.account.coins[coin]['balance']
            if 0.0 < coin_val < 1.0:
                balance = str(format(static.account.coins[coin]['balance'], '.6f'))
            else:
                balance = str(format(static.account.coins[coin]['balance'], '.1f'))
        self.sell_orderable_1.setText(balance)
        self.sell_orderable_2.setText(balance)
        self.sell_orderable_3.setText(balance)

        # refresh price
        self.all_reset()
        self.buy_price_1.setValue(market_price)
        self.buy_price_3.setValue(market_price)
        self.sell_price_1.setValue(market_price)
        self.sell_price_3.setValue(market_price)

    def set_current_price(self, cur_price):
        self.buy_price_1.setValue(cur_price)
        self.buy_price_3.setValue(cur_price)
        self.sell_price_1.setValue(cur_price)
        self.sell_price_3.setValue(cur_price)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = TradeWidget()
    window.show()
    sys.exit(app.exec_())
