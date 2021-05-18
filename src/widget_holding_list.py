# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

import static
import utils

class HoldingListWorker(QThread):
    dataSent = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.alive = False

    def run(self):
        self.alive = True
        while self.alive:
            time.sleep(1)
            self.dataSent.emit(static.account.coins)
            
    def close(self):
        self.alive = False
        super().terminate()

class HoldingListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(utils.get_file_path("styles/ui/holding_list.ui"), self)

        #참고 QHeaderView Class
        self.hold_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.hold_list.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.count_codes = len(static.account.coins)
        print(self.count_codes)

        self.hw = HoldingListWorker()
        self.hw.dataSent.connect(self.updataData)
        self.hw.start()

    def updataData(self, data):
        self.color_red = QBrush(QColor(207, 48, 74))  # CF304A
        self.color_green = QBrush(QColor(2, 192, 118))  # 02C076
        self.color_white = QBrush(QColor(255, 255, 255))

        self.hold_list.clearContents()
        self.hold_list.setRowCount(len(data))

        font = QFont()
        font.setBold(True)
        for i, coin in enumerate(data):
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            item.setText(static.chart.get_coin(f'{static.FIAT}-{coin}').korean_name + '(' + coin + ')')
            item.setFont(font)
            self.hold_list.setItem(i, 0, item)

            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            if data[coin]['yield'] < 0 :
                item.setForeground(self.color_red)
            elif data[coin]['yield'] > 0 :
                item.setForeground(self.color_green)
            
            item.setText(str(data[coin]['yield']))
            self.hold_list.setItem(i, 1, item)
    
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.hw.close()
        return super().closeEvent(a0)
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    GUI = HoldingListWidget()
    GUI.show()
    sys.exit(app.exec_())
