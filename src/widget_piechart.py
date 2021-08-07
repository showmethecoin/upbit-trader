# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
from PyQt5.QtCore import QThread

from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import static

class PieWorker(QThread):
    def __init__(self, canvas):
        super().__init__()
        self.alive = False
        self.canvas = canvas
        
    def run(self):
        self.alive = True
        while self.alive:
            time.sleep(1)
            self.draw_piechart()
    
    def draw_piechart(self):
        cash =int(static.account.cash + static.account.locked_cash)
        sum = cash
        datas = [[cash, 'KRW']]
        for i in static.account.coins:
            datas.append([int(static.account.coins[i]['evaluate']), i])
            sum += int(static.account.coins[i]['evaluate'])
        
        # Sort Coin and KRW
        datas.sort(reverse=True)
        remain = [0,'Other Coins']
        
        labels = []
        frequency = []

        if sum != 0:
        # Data Screening
            for i in datas:
                if len(labels) < 7 or i[1] == 'KRW':
                    labels.append(i[1] + " : " + str(round(i[0]/sum * 100)) + "%")
                    frequency.append(i[0])
                else:
                    remain[0] += i[0]
            
            # If there are any remaining coins
            if remain[0] != 0:
                labels.append(remain[1] + " : " + str(round(remain[0]/sum * 100)) + "%")
                frequency.append(remain[0])

            self.canvas.axes.clear()
            self.canvas.axes2.clear()
        else:
            labels.append("KRW : 100%")
            frequency.append(100)

        # Donut Chart
        pie = self.canvas.axes.pie(frequency, ## 파이차트 출력
                startangle=90, ## 시작점을 90도(degree)로 지정
                counterclock=False, ## 시계 방향으로 그린다.
                #autopct=lambda p : str(round(p)) + "%", ## 퍼센티지 출력
                wedgeprops=dict(width=0.5) ## 중간의 반지름 0.5만큼 구멍을 뚫어준다.
                )
        
        # Pie Chart
        # pie = self.axes.pie(frequency, startangle=260, counterclock=False, explode=explode)

        # Set Chart Percentage text
        # for t in pie[2]:
        #     t.set_color("white")
        #     t.set_fontweight('bold')

        # Set Legend
        self.canvas.axes2.legend(pie[0],labels, loc = 'center',labelcolor='white',  borderpad=1, fontsize = 12)
        self.canvas.axes2.axis('off')
        self.canvas.draw_idle()
            

    def close(self) -> None:
        self.alive = False
        return super().terminate()
    

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=12, height=8):
        plt.rcParams['axes.facecolor'] = '31363b'
        plt.rcParams['axes.edgecolor'] = 'ffffff'
        plt.rcParams['xtick.color'] = 'ffffff'
        plt.rcParams['ytick.color'] = 'ffffff'
        self.fig = Figure(figsize=(width, height))
        self.fig.set_facecolor('#31363b')
        self.fig.set_edgecolor('#ffffff')
        self.axes = self.fig.add_subplot(1,2,1)
        self.axes2 = self.fig.add_subplot(1,2,2)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)


class PieChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Canvas Initialize
        self.canvas = MyMplCanvas(self, width=7, height=3)
        self.pw = PieWorker(self.canvas)
        self.pw.draw_piechart()
    
    # close thread
    def closeEvent(self, event):
        self.pw.close()

if __name__ == "__main__":
    import sys
    from utils import set_windows_selector_event_loop_global
    set_windows_selector_event_loop_global()

    qApp = QApplication(sys.argv)
    aw = PieChartWidget()

    aw.show()
    sys.exit(qApp.exec_())

