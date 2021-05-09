# !/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5 import uic

import static
import utils


class TradeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(utils.get_file_path("styles/ui/trade.ui"), self)
        self.set_price('KRW-BTC')

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

        # SELL Reset-Button Clicked Listener Initialize
        self.sell_reset_1.clicked.connect(self.clicked_reset)
        self.sell_reset_2.clicked.connect(self.clicked_reset)
        self.sell_reset_3.clicked.connect(self.clicked_reset)

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
                self.buy_volume_2.setValue(0.0)
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
                self.sell_volume_2.setValue(0.0)
            # Reservation
            else:
                self.sell_price_3.setValue(0.0)
                self.sell_volume_3.setValue(0.0)
                self.sell_total_price_3.setValue(0.0)
                self.sell_monitor_price_3.setValue(0.0)

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
                    self.buy_total_price_1.value() / self.buy_price_1.value())
            # Reservation
            elif self.buy_price_3.value() != 0.0:
                self.buy_volume_3.setValue(
                    self.buy_total_price_3.value() / self.buy_price_3.value())

        # SELL
        else:
            idx = self.sell_stack.currentIndex()

            # Designation
            if idx == 0 and self.sell_price_1.value() != 0.0:
                self.sell_volume_1.setValue(
                    self.sell_total_price_1.value() / self.sell_price_1.value())
            # Reservation
            elif self.sell_price_3.value() != 0.0:
                self.sell_volume_3.setValue(
                    self.sell_total_price_3.value() / self.sell_price_3.value())

    # Calc Latest Total-Price
    def set_total_price(self):
        # BUY
        if self.tabWidget.currentIndex() == 0:
            idx = self.buy_stack.currentIndex()

            # Designation
            if idx == 0:
                self.buy_total_price_1.setValue(
                    self.buy_price_1.value() * self.buy_volume_1.value())
            # Reservation
            else:
                self.buy_total_price_3.setValue(
                    self.buy_price_3.value() * self.buy_volume_3.value())

        # SELL
        else:
            idx = self.sell_stack.currentIndex()

            # Designation
            if idx == 0:
                self.sell_total_price_1.setValue(
                    self.sell_price_1.value() * self.sell_volume_1.value())
            # Reservation
            else:
                self.sell_total_price_3.setValue(
                    self.sell_price_3.value() * self.sell_volume_3.value())

    # All Reset
    def all_reset(self):
        self.buy_price_1.setValue(0.0)
        self.buy_volume_1.setValue(0.0)
        self.buy_total_price_1.setValue(0.0)
        self.buy_volume_2.setValue(0.0)
        self.buy_price_3.setValue(0.0)
        self.buy_volume_3.setValue(0.0)
        self.buy_total_price_3.setValue(0.0)
        self.buy_monitor_price_3.setValue(0.0)
        self.sell_price_1.setValue(0.0)
        self.sell_volume_1.setValue(0.0)
        self.sell_total_price_1.setValue(0.0)
        self.sell_volume_2.setValue(0.0)
        self.sell_price_3.setValue(0.0)
        self.sell_volume_3.setValue(0.0)
        self.sell_total_price_3.setValue(0.0)
        self.sell_monitor_price_3.setValue(0.0)

    # Set Price
    def set_price(self, ticker):
        if static.chart == None:
            return
        price = static.chart.coins[ticker].get_trade_price()
        self.all_reset()
        self.buy_price_1.setValue(price)
        self.buy_price_3.setValue(price)
        self.sell_price_1.setValue(price)
        self.sell_price_3.setValue(price)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = TradeWidget()
    window.show()
    sys.exit(app.exec_())
