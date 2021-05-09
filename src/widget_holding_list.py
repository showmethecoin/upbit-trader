# !/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import utils


class HoldingListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(utils.get_file_path("styles/ui/holding_list.ui"), self)
        #화면 수직,수평으로 늘릴 경우 칸에 맞게 변경됨
        #사용 가능한 공간을 채우기 위해 섹션의 크기를 자동으로 조정
        #참고 QHeaderView Class
        self.hold_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hold_list.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    GUI = HoldingListWidget()
    GUI.show()
    sys.exit(app.exec_())
