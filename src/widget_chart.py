# !/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio as aio

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick2_ohlc
import aiopyupbit

from static import log

class CandleWorker(QThread):
    def __init__(self, canvas, code, count):
        super().__init__()
        self.alive = False
        self.canvas = canvas
        self.code = code
        self.count = count
        
    def run(self) -> None:
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        loop.run_until_complete(self.__loop())
    
    def close(self) -> None:
        self.alive = False
        return super().terminate()
    
    async def __loop(self):
        while self.alive:
            try:
                await aio.sleep(0.5)
                df = await aiopyupbit.get_ohlcv(ticker=self.code, 
                                                interval="minutes1", 
                                                count=self.count)
                # clear chart
                self.canvas.axes.clear()
                # set chart
                candlestick2_ohlc(self.canvas.axes, 
                            df['open'], 
                            df['high'],
                            df['low'], 
                            df['close'], 
                            width=0.5, 
                            colorup='#02C076', 
                            colordown='#CF304A')
                # draw chart
                self.canvas.draw_idle()
            except Exception as e:
                log.error(e)

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=12, height=8):
        plt.rcParams['axes.facecolor'] = '31363b'
        plt.rcParams['axes.edgecolor'] = 'ffffff'
        plt.rcParams['xtick.color'] = 'ffffff'
        plt.rcParams['ytick.color'] = 'ffffff'
        self.fig = Figure(figsize=(width, height))
        self.fig.set_facecolor('#31363b')
        self.fig.set_edgecolor('#ffffff')
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)


class CandleChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.idx = 0
        # Button Initialize
        self.expansion_button = QPushButton("+", self)
        self.reduction_button = QPushButton("-", self)
        self.expansion_button.clicked.connect(self.on_expansion)
        self.reduction_button.clicked.connect(self.on_reduction)

        # Canvas Initialize
        self.canvas = MyMplCanvas(self, width=5, height=3)
        self.cw = CandleWorker(self.canvas, 'KRW-BTC', 15)

        # Assign Element Location
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        hbox = QHBoxLayout()
        hbox.addWidget(self.expansion_button)
        hbox.addWidget(self.reduction_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
    
    # expansion button clicked
    def on_expansion(self):
        if self.cw.count < 200:
            self.cw.count += 5

    # reduction button clicked
    def on_reduction(self):
        if self.cw.count > 15:
            self.cw.count -= 5  
    
    # changed Coin
    def set_coin(self, code):
        self.cw.code = code
    
    # close thread
    def closeEvent(self, event):
        self.cw.close()

if __name__ == "__main__":
    import sys
    from multiprocessing import freeze_support
    from utils import set_windows_selector_event_loop_global

    freeze_support()
    set_windows_selector_event_loop_global()

    qApp = QApplication(sys.argv)
    aw = CandleChartWidget()

    aw.show()
    sys.exit(qApp.exec_())
