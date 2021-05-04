import time
import sys, os, random
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import mpl_finance as mpf
import json
import random
from pyupbit.quotation_api import get_ohlcv
import requests
import pandas as pd
import mpl_finance
import datetime
import pyupbit
import matplotlib.ticker as ticker

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
    def __init__(self,parent = None):
        super().__init__(parent)
        self.idx = 0
        vbox = QVBoxLayout()
        self.canvas = MyMplCanvas(self, width=5, height=3, dpi=100)
        self.count = 15
        self.coin = 'KRW-BTC'
        vbox.addWidget(self.canvas)
        hbox = QHBoxLayout()
        self.expansion_button = QPushButton("+", self)
        self.reduction_button = QPushButton("-", self)
        self.expansion_button.clicked.connect(self.on_expansion)
        self.reduction_button.clicked.connect(self.on_reduction)
        hbox.addWidget(self.expansion_button)
        hbox.addWidget(self.reduction_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.get_chart()
        self.ani = animation.FuncAnimation(self.canvas.fig, self.animate,interval=1000)

    # animation function
    def animate(self, t):
        self.canvas.axes.clear()
        self.get_chart()
    # chart update
    def get_chart(self):
        df = get_ohlcv(ticker=self.coin, interval="minutes1", count=self.count, to=None)
        print(self.idx)
        self.idx+= 1
        mpl_finance.candlestick2_ohlc(self.canvas.axes, df['open'], df['high'], df['low'], df['close'], width=0.5, colorup='r', colordown='g')


    def on_expansion(self):
        if self.count < 200:
            self.count += 5
    
    def on_reduction(self):
        if self.count > 15:
            self.count -= 5

if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    aw = CandleChartWidget()
    
    aw.show()
    sys.exit(qApp.exec_())