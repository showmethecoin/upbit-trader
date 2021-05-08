import sys
import time

from component import RealtimeManager, Coin
import static
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QTableWidgetItem, QProgressBar
from PyQt5.QtCore import QPropertyAnimation, Qt, QThread, pyqtSignal


class OrderbookWorker(QThread):
    dataSent = pyqtSignal(Coin)

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
        uic.loadUi("./src/ui/orderbook.ui", self)
    
        #화면 수직,수평으로 늘릴 경우 칸에 맞게 변경됨
        #사용 가능한 공간을 채우기 위해 섹션의 크기를 자동으로 조정
        #참고 QHeaderView Class
        self.tableAsks.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableBids.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableAsks.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableBids.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ticker = ticker

        self.asksAnim = [ ]
        self.bidsAnim = [ ]
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
        
        # asks테이블 값 설정
        for i ,v in enumerate(data[::-1]):
            item_0 = self.tableAsks.item(i, 0)
            item_0.setText(f"{round(v['ap'],3):,}")

            item_1 = self.tableAsks.cellWidget(i, 1)
            # 범위가 int형으로 들어가기 때문에(값이 낮아서 전부 0으로 되는 문제)
            # 소수 3째자리 까지 표현하므로 범위값에 1000을 곱해서 범위를 지정해줌
            item_1.setRange(0, 100)
            item_1.setFormat(f"{round(v['as'],3):,}")
            self.asksAnim[i].setStartValue(v['as']/asks_size)
            self.asksAnim[i].setEndValue(v['as']/asks_size)
            self.asksAnim[i].start()

        # bids테이블 값 설정
        for i ,v in enumerate(data):
            item_0 = self.tableBids.item(i, 0)
            item_0.setText(f"{round(v['bp'],3):,}")
           
            item_1 = self.tableBids.cellWidget(i, 1)
            item_1.setRange(0, 100)
            item_1.setFormat(f"{round(v['bs'],3):,}")
            self.bidsAnim[i].setStartValue(v['bs']/bids_size)
            self.bidsAnim[i].setEndValue(v['bs']/bids_size)
            self.bidsAnim[i].start()

    def closeEvent(self, event):
        self.ow.close()

 
if __name__ == "__main__":
    import sys
    #from PyQt5.QtWidgets import QApplication
    from PySide2.QtWidgets import QApplication
    static.chart = RealtimeManager()
    static.chart.start()
    app = QApplication(sys.argv)
    ow = OrderbookWidget()
    ow.show()
    #cw = test_chart_list.ChartlistWidget()
    #cw.show()
    exit(app.exec_())