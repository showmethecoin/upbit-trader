# !/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio as aio
import datetime
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import static
from utils import get_file_path
from db import DBHandler


class SignalListWorker(QThread):
    dataSent = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.alive = False

    def run(self) -> None:
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        self.db = DBHandler(ip=static.config.mongo_ip,
                            port=static.config.mongo_port,
                            id=static.config.mongo_id,
                            password=static.config.mongo_password,
                            loop=loop)
        loop.run_until_complete(self.__loop())

    def close(self) -> None:
        self.alive = False
        return super().terminate()

    async def __loop(self):
        while self.alive:
            await aio.sleep(0.5)
            data = await self.db.find_item(condition=None, db_name='signal_history', 
                                           collection_name=datetime.datetime.today().strftime("%Y-%m-%d"))
            data = data.sort('time', -1)
            data = await data.to_list(length=None)
            data_df = pd.DataFrame(data)
            self.dataSent.emit(data_df)


class SignallistWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(get_file_path("styles/ui/signal_list.ui"), self)
        self.signallist.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.items = []
        self.sw = SignalListWorker()
        self.sw.dataSent.connect(self.set_table)

    def set_table(self, data):
        table = self.signallist
        items = self.items
        if table.rowCount() == len(data):
            return

        table.clearContents()  # 테이블 지우고
        table.setRowCount(len(data))

        # 찍을 데이터가 없는 경우
        if len(data) == 0:
            return

        # 동적으로 row관리

        count_data = len(data)
        font = QFont()
        font.setBold(True)

        for i in range(count_data):

            if(i >= len(items)):
                items.append([QTableWidgetItem(), QTableWidgetItem(), QTableWidgetItem(
                ), QTableWidgetItem(), QTableWidgetItem(), QTableWidgetItem()])
                items[i][0].setFont(font)
                items[i][0].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                items[i][1].setFont(font)
                items[i][1].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                items[i][2].setFont(font)
                items[i][2].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                items[i][3].setFont(font)
                items[i][3].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                items[i][4].setFont(font)
                items[i][4].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                items[i][5].setFont(font)
                items[i][5].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            items[i][0].setText(data['code'][i])
            items[i][1].setText(str(data['time'][i]))
            if data['position'][i] == 'bid':
                items[i][2].setText('매수')
            else:
                items[i][2].setText('매도')

            if data['type'][i] == 'limit':
                items[i][3].setText('지정가')
            else:
                items[i][3].setText('시장가')
            items[i][4].setText(str(data['price'][i]))
            items[i][5].setText(str(i))

            table.setItem(i, 0, items[i][0])
            table.setItem(i, 1, items[i][1])
            table.setItem(i, 2, items[i][2])
            table.setItem(i, 3, items[i][3])
            table.setItem(i, 4, items[i][4])
            table.setItem(i, 5, items[i][5])

        # table.verticalHeader().setDefaultSectionSize(60)

    def closeEvent(self, event):
        self.sw.close()


if __name__ == "__main__":
    import sys
    from component import RealtimeManager, Account
    from utils import set_windows_selector_event_loop_global
    import aiopyupbit
    from config import Config

    set_windows_selector_event_loop_global()

    static.config = Config()
    static.config.load()

    loop = aio.new_event_loop()
    aio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=static.FIAT, contain_name=True))
    static.chart = RealtimeManager(codes=codes)
    static.chart.start()

    # Upbit account
    static.account = Account(access_key=static.config.upbit_access_key,
                             secret_key=static.config.upbit_secret_key)
    static.account.start()

    app = QApplication(sys.argv)
    GUI = SignallistWidget()
    GUI.show()
    sys.exit(app.exec_())
