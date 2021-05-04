import sys
import time
import pyupbit
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QTableWidgetItem, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation

class OrderbookWorker(QThread):
    dataSent = pyqtSignal(list)

    def __init__(self, ticker):
        super().__init__()
        self.size = 10
        self.ticker = ticker
        self.alive = True

    def run(self):
        while self.alive:
            data = pyupbit.get_orderbook("KRW-"+self.ticker)
            time.sleep(0.2)
            if data != None:
                self.dataSent.emit(data)

    def close(self):
        self.alive = False

class OrderbookWidget(QWidget):
    def __init__(self, parent=None, ticker="BTC"):
        super().__init__(parent)
        uic.loadUi("./src/ui/orderbook.ui", self)
        
        #화면 수직,수평으로 늘릴 경우 칸에 맞게 변경됨
        #사용 가능한 공간을 채우기 위해 섹션의 크기를 자동으로 조정
        #참고 QHeaderView Class
        self.tableAsks.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableBids.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableAsks.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableBids.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        #self.tableAsks.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #self.tableBids.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        #loadUi("orderbook.ui", self)
        self.ticker = ticker

        self.asksAnim = [ ]
        self.bidsAnim = [ ]
        for i in range(self.tableBids.rowCount()):
            # 매도호가
            item_0 = QTableWidgetItem(str(""))
            item_0.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableAsks.setItem(i, 0, item_0)

            item_1 = QTableWidgetItem(str(""))
            item_1.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableAsks.setItem(i, 1, item_1)

            item_2 = QProgressBar(self.tableAsks)
            item_2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_2.setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0%);border : 1}
                QProgressBar::Chunk {background-color : rgba(255, 0, 0, 50%);border : 1}
            """)
            self.tableAsks.setCellWidget(i, 2, item_2)
            
            anim = QPropertyAnimation(item_2, b"value")
            anim.setDuration(200)
            self.asksAnim.append(anim)
            
            # 매수호가
            item_0 = QTableWidgetItem(str(""))
            item_0.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableBids.setItem(i, 0, item_0)

            item_1 = QTableWidgetItem(str(""))
            item_1.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableBids.setItem(i, 1, item_1)

            item_2 = QProgressBar(self.tableBids)
            item_2.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_2.setStyleSheet("""
                QProgressBar {background-color : rgba(0, 0, 0, 0%);border : 1}
                QProgressBar::Chunk {background-color : rgba(0, 255, 0, 40%);border : 1}
            """)
            self.tableBids.setCellWidget(i, 2, item_2)
            anim = QPropertyAnimation(item_2, b"value")
            anim.setDuration(200)
            self.bidsAnim.append(anim)
        self.ow = OrderbookWorker(self.ticker)
        self.ow.dataSent.connect(self.updateData)
        self.ow.start()

    def updateData(self, data):
        #print(data[0]['orderbook_units'])
        data = data[0]['orderbook_units']
        # 아래 코드에서 적용될 수 있게 data 형태를 바꿔줌
        data_dict = {}

        # 먼저 리스트로 변경하고 나중에 dict에 추가
        asks_tmp = []
        bids_tmp = []

        for i in range(10):
            asks_tmp.append( { 'price' : data[i]['ask_price'], 'quantity' : round(data[i]['ask_size'], 3) } )
            bids_tmp.append( { 'price' : data[i]['bid_price'], 'quantity' : round(data[i]['bid_size'], 3) } )
        
        data_dict['asks'] = asks_tmp
        data_dict['bids'] = bids_tmp
        
        data = data_dict

        # bid의 progressbar표현하기 위한 값 계산
        bids_tradingValues = [ ]
        asks_tradingValues = [ ]
        for v in data['bids']:
            bids_tradingValues.append(round(v['price'] * v['quantity'] / 10000, 3))
        bids_maxtradingValue = max(bids_tradingValues)
       
        for a in data['asks'][::-1]:
            asks_tradingValues.append(round(a['price'] * a['quantity'] / 10000, 3))
        asks_maxtradingValue = max(asks_tradingValues)


        #print(maxtradingValue)

        for i, v in enumerate(data['asks'][::-1]):
            item_0 = self.tableAsks.item(i, 0)
            item_0.setText(f"{v['price']:,}")
            item_1 = self.tableAsks.item(i, 1)
            item_1.setText(f"{v['quantity']:,}")
            item_2 = self.tableAsks.cellWidget(i, 2)
            item_2.setRange(0, asks_maxtradingValue)
            item_2.setFormat(f"{asks_tradingValues[i]:,}")
            self.asksAnim[i].setStartValue(asks_tradingValues[i])
            self.asksAnim[i].setEndValue(asks_tradingValues[i])
            self.asksAnim[i].start()

        for i, v in enumerate(data['bids']):
            item_0 = self.tableBids.item(i, 0)
            item_0.setText(f"{v['price']:,}")
            item_1 = self.tableBids.item(i, 1)
            item_1.setText(f"{v['quantity']:,}")
            item_2 = self.tableBids.cellWidget(i, 2)
            item_2.setRange(0, bids_maxtradingValue)
            item_2.setFormat(f"{bids_tradingValues[i]:,}")
            self.bidsAnim[i].setStartValue(bids_tradingValues[i])
            self.bidsAnim[i].setEndValue(bids_tradingValues[i])
            self.bidsAnim[i].start()
            
        

    def closeEvent(self, event):
        self.ow.close()


if __name__ == "__main__":
    import sys
    #from PyQt5.QtWidgets import QApplication
    from PySide2.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ow = OrderbookWidget()
    ow.show()
    #cw = test_chart_list.ChartlistWidget()
    #cw.show()
    exit(app.exec_())