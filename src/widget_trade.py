import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pyupbit
import ui_styles
import static
from ui_trade import Ui_Form
from component import Chart

class TradeWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent=parent)
        #uic.loadUi("orderbook.ui", self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.set_price('KRW-BTC')

        # BUY Radio Clicked Listener Initiallize
        self.ui.buy_designation_price.setChecked(True)
        self.ui.buy_designation_price.clicked.connect(self.clicked_buy_designation_price)
        self.ui.buy_market_price.clicked.connect(self.clicked_buy_market_pice)
        self.ui.buy_reservation_price.clicked.connect(self.clicked_buy_reservation_pice)

        # SELL Radio Clicked Listener Initiallize
        self.ui.sell_designation_price.setChecked(True)
        self.ui.sell_designation_price.clicked.connect(self.clicked_sell_designation_price)
        self.ui.sell_market_price.clicked.connect(self.clicked_sell_market_pice)
        self.ui.sell_reservation_price.clicked.connect(self.clicked_sell_reservation_pice)

        # BUY Reset-Button Clicked Listener Initiallize
        self.ui.buy_reset_1.clicked.connect(self.clicked_reset)
        self.ui.buy_reset_2.clicked.connect(self.clicked_reset)
        self.ui.buy_reset_3.clicked.connect(self.clicked_reset)

        # SELL Reset-Button Clicked Listener Initiallize
        self.ui.sell_reset_1.clicked.connect(self.clicked_reset)
        self.ui.sell_reset_2.clicked.connect(self.clicked_reset)
        self.ui.sell_reset_3.clicked.connect(self.clicked_reset)
        
        # BUY Price Changed Listener Initiallize
        self.ui.buy_price_1.setGroupSeparatorShown(True)
        self.ui.buy_price_1.textChanged.connect(self.changed_price)
        self.ui.buy_volume_1.textChanged.connect(self.changed_volume)
        self.ui.buy_total_price_1.textChanged.connect(self.changed_total)
        self.ui.buy_price_3.textChanged.connect(self.changed_price)
        self.ui.buy_volume_3.textChanged.connect(self.changed_volume)
        self.ui.buy_total_price_3.textChanged.connect(self.changed_total)

        # SELL Price Changed Listener Initiallize
        self.ui.sell_price_1.textChanged.connect(self.changed_price)
        self.ui.sell_volume_1.textChanged.connect(self.changed_volume)
        self.ui.sell_total_price_1.textChanged.connect(self.changed_total)
        self.ui.sell_price_3.textChanged.connect(self.changed_price)
        self.ui.sell_volume_3.textChanged.connect(self.changed_volume)
        self.ui.sell_total_price_3.textChanged.connect(self.changed_total)

    # Clicked Event Function
    def clicked_buy_designation_price(self):
        self.ui.buy_stack.setCurrentIndex(0)
    def clicked_buy_market_pice(self):
        self.ui.buy_stack.setCurrentIndex(1)
    def clicked_buy_reservation_pice(self):
        self.ui.buy_stack.setCurrentIndex(2)
    def clicked_sell_designation_price(self):
        self.ui.sell_stack.setCurrentIndex(0)
    def clicked_sell_market_pice(self):
        self.ui.sell_stack.setCurrentIndex(1)
    def clicked_sell_reservation_pice(self):
        self.ui.sell_stack.setCurrentIndex(2)
                
    def clicked_reset(self):
         # BUY
        if self.ui.tabWidget.currentIndex() == 0:
            idx = self.ui.buy_stack.currentIndex()

            # Designation
            if idx == 0:
                self.ui.buy_price_1.setValue(0.0)
                self.ui.buy_volume_1.setValue(0.0)
                self.ui.buy_total_price_1.setValue(0.0)
            # Market
            elif idx == 1:
                self.ui.buy_volume_2.setValue(0.0)
            # Reservation 
            else:
                self.ui.buy_price_3.setValue(0.0)
                self.ui.buy_volume_3.setValue(0.0)
                self.ui.buy_total_price_3.setValue(0.0)
                self.ui.buy_monitor_price_3.setValue(0.0)
        # SELL
        else :
            idx = self.ui.sell_stack.currentIndex()

            # Designation
            if idx == 0:
                self.ui.sell_price_1.setValue(0.0)
                self.ui.sell_volume_1.setValue(0.0)
                self.ui.sell_total_price_1.setValue(0.0)
            # Market
            elif idx == 1:
                self.ui.sell_volume_2.setValue(0.0)
            # Reservation 
            else:
                self.ui.sell_price_3.setValue(0.0)
                self.ui.sell_volume_3.setValue(0.0)
                self.ui.sell_total_price_3.setValue(0.0)
                self.ui.sell_monitor_price_3.setValue(0.0)

    # Change Event Function
    def changed_price(self):
        self.set_total_price()           
    def changed_volume(self):
        self.set_total_price()
    def changed_total(self):
        # BUY
        if self.ui.tabWidget.currentIndex() == 0:
            idx = self.ui.buy_stack.currentIndex()

            # Designation
            if idx == 0 and self.ui.buy_price_1.value() != 0.0:
                self.ui.buy_volume_1.setValue(self.ui.buy_total_price_1.value() / self.ui.buy_price_1.value())
            # Reservation 
            elif self.ui.buy_price_3.value() != 0.0:
                self.ui.buy_volume_3.setValue(self.ui.buy_total_price_3.value() / self.ui.buy_price_3.value())
        
        # SELL
        else :
            idx = self.ui.sell_stack.currentIndex()

            # Designation
            if idx == 0 and self.ui.sell_price_1.value() != 0.0:
                self.ui.sell_volume_1.setValue(self.ui.sell_total_price_1.value() / self.ui.sell_price_1.value())
            # Reservation 
            elif self.ui.sell_price_3.value() != 0.0 :
                self.ui.sell_volume_3.setValue(self.ui.sell_total_price_3.value() / self.ui.sell_price_3.value())
    
    # Calc Latest Total-Price
    def set_total_price(self) :
        # BUY
        if self.ui.tabWidget.currentIndex() == 0:
            idx = self.ui.buy_stack.currentIndex()

            # Designation
            if idx == 0 :
                self.ui.buy_total_price_1.setValue(self.ui.buy_price_1.value() * self.ui.buy_volume_1.value())
            # Reservation 
            else :
                self.ui.buy_total_price_3.setValue(self.ui.buy_price_3.value() * self.ui.buy_volume_3.value())
        
        # SELL
        else :
            idx = self.ui.sell_stack.currentIndex()

            # Designation
            if idx == 0 :
                self.ui.sell_total_price_1.setValue(self.ui.sell_price_1.value() * self.ui.sell_volume_1.value())
            # Reservation 
            else :
                self.ui.sell_total_price_3.setValue(self.ui.sell_price_3.value() * self.ui.sell_volume_3.value())
    
    # All Reset
    def all_reset(self):
        self.ui.buy_price_1.setValue(0.0)
        self.ui.buy_volume_1.setValue(0.0)
        self.ui.buy_total_price_1.setValue(0.0)
        self.ui.buy_volume_2.setValue(0.0)
        self.ui.buy_price_3.setValue(0.0)
        self.ui.buy_volume_3.setValue(0.0)
        self.ui.buy_total_price_3.setValue(0.0)
        self.ui.buy_monitor_price_3.setValue(0.0)
        self.ui.sell_price_1.setValue(0.0)
        self.ui.sell_volume_1.setValue(0.0)
        self.ui.sell_total_price_1.setValue(0.0)
        self.ui.sell_volume_2.setValue(0.0)
        self.ui.sell_price_3.setValue(0.0)
        self.ui.sell_volume_3.setValue(0.0)
        self.ui.sell_total_price_3.setValue(0.0)
        self.ui.sell_monitor_price_3.setValue(0.0)
    
    # Set Price
    def set_price(self, ticker):
        if static.chart == None :
            return
        price = static.chart.coins[ticker].get_trade_price()
        self.all_reset()
        self.ui.buy_price_1.setValue(price)
        self.ui.buy_price_3.setValue(price)
        self.ui.sell_price_1.setValue(price)
        self.ui.sell_price_3.setValue(price)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradeWidget()
    window.show()
    sys.exit(app.exec_())