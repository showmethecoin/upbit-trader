# !/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import multiprocessing

from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick2_ohlc
import aiopyupbit

import utils

class CandleSender(multiprocessing.Process):
    def __init__(self,
                 in_queue:multiprocessing.Queue,
                 out_queue: multiprocessing.Queue):
        # Public
        self.alive = False
        # Private
        self.__in_queue = in_queue
        self.__out_queue = out_queue
        
        super().__init__()
        
    def run(self) -> None:
        self.alive = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__loop())
    
    def terminate(self) -> None:
        self.alive = False
        return super().terminate()
    
    async def __loop(self):
        data = self.__in_queue.get()
        while self.alive:
            try:
                if not self.__in_queue.empty():
                    data = self.__in_queue.get()
                df = await aiopyupbit.get_ohlcv(ticker=data['code'], 
                                                interval="minutes1", 
                                                count=data['count'])
                self.__out_queue.put(df)
            except:
                pass
        

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=12, height=8, dpi=100):
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
        self.expansion_button = QPushButton("+", self)
        self.reduction_button = QPushButton("-", self)
        self.expansion_button.clicked.connect(self.on_expansion)
        self.reduction_button.clicked.connect(self.on_reduction)
        self.count = 15
        self.code = 'KRW-BTC'
        self.canvas = MyMplCanvas(self, width=5, height=3, dpi=100)
        self.ani = animation.FuncAnimation(self.canvas.fig, 
                                           self.animate, 
                                           interval=500)
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        hbox = QHBoxLayout()
        hbox.addWidget(self.expansion_button)
        hbox.addWidget(self.reduction_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        
        self.__in_queue = multiprocessing.Queue()
        self.__out_queue = multiprocessing.Queue()
        self.candle_sender = CandleSender(in_queue=self.__in_queue,
                                          out_queue=self.__out_queue)
        self.__in_queue.put({'code':self.code, 'count': self.count})
        self.candle_sender.start()

    # animation function
    def animate(self, t):
        self.canvas.axes.clear()
        self.get_chart()

    # chart update
    def get_chart(self):
        df = self.__out_queue.get()
        if isinstance(df, type(None)):
            df = self.before_df
        else:
            self.before_df = df
        try:
            candlestick2_ohlc(self.canvas.axes, 
                            df['open'], 
                            df['high'],
                            df['low'], 
                            df['close'], 
                            width=0.5, 
                            colorup='#02C076', 
                            colordown='#CF304A')
        except:
            pass

    def on_expansion(self):
        if self.count < 200:
            self.count += 5
        self.clear_in_queue()
        self.__in_queue.put({'code':self.code, 'count': self.count})
        self.clear_out_queue()

    def on_reduction(self):
        if self.count > 15:
            self.count -= 5  
        self.clear_in_queue()
        self.__in_queue.put({'code':self.code, 'count': self.count})
        self.clear_out_queue()
        
    def set_coin(self, code):
        self.code = code
        self.clear_in_queue()
        self.__in_queue.put({'code':self.code, 'count': self.count})
        self.clear_out_queue()
    
    def clear_in_queue(self):
        while not self.__in_queue.empty():
            self.__in_queue.get_nowait()
    
    def clear_out_queue(self):
        while not self.__out_queue.empty():
            self.__out_queue.get_nowait()

    # TODO CandleSender 안꺼지는데 추가좀
    def close(self) -> bool:
        self.candle_sender.terminate()
        return super().close()
        


if __name__ == "__main__":
    import sys

    multiprocessing.freeze_support()
    utils.set_windows_selector_event_loop_global()

    qApp = QApplication(sys.argv)
    aw = CandleChartWidget()

    aw.show()
    sys.exit(qApp.exec_())
