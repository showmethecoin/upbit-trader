# !/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5 import uic

from strategy import VariousIndicatorStrategy, VolatilityBreakoutStrategy
from utils import get_file_path
import static


class SettingsWidget(QWidget):
    def __init__(self, parent=None,):
        super().__init__(parent)
        uic.loadUi(get_file_path('styles/ui/settings.ui'), self)
        self.close_btn.clicked.connect(self.close_btn_click)
        self.minimize_btn.clicked.connect(lambda: self.showMinimized())
        self.start.clicked.connect(self.clicked_start)
        self.stop.clicked.connect(self.clicked_stop)
        self.setWindowFlag(Qt.FramelessWindowHint)

        if static.config.settings_auto_trading == False:
            self.stop.setStyleSheet("""
                QPushButton
                {
                    color: #eff0f1;
                    background-color: #757575;
                }
            """)
            self.stop.setEnabled(False)
        else:
            self.start.setStyleSheet("""
                QPushButton
                {
                    color: #eff0f1;
                    background-color: #757575;
                }
            """)
            self.RSI.setEnabled(False)
            self.Volatility.setEnabled(False)
            self.start.setEnabled(False)
        
        if static.config.strategy_type == 'VolatilityBreakout':
            self.RSI.setChecked(True)
            static.config.strategy_type = 'VolatilityBreakout'
        else:
            self.Volatility.setChecked(True)
            static.config.strategy_type = 'VariousIndicator'

        # MouseLeftClick Event Listener
        def mousePressEvent(event):
            if event.buttons() == Qt.LeftButton:
                self.dragPos = event.globalPos()
                event.accept()

        # MouseClickMove Event Listener
        def moveWindow(event):
            # IF MAXIMIZED CHANGE TO NORMAL
            if self.status == 1:
                self.status = 0
                self.showNormal()
            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        # Link events to Titlebar
        self.toplabel_title.mousePressEvent = mousePressEvent
        self.toplabel_title.mouseMoveEvent = moveWindow

    def close_btn_click(self):
        static.settings_start = False
        self.close()

    def clicked_start(self):
        if self.RSI.isChecked():
            static.config.strategy_type = 'VolatilityBreakout'
            static.strategy = VolatilityBreakoutStrategy(queue=static.signal_queue)
        else:
            static.config.strategy_type = 'VariousIndicator'
            static.strategy = VariousIndicatorStrategy(queue=static.signal_queue)
        static.config.settings_auto_trading = True
        static.settings_start = False
        static.config.save()
        static.strategy.start()
        self.close()
    
    def clicked_stop(self):
        static.config.settings_auto_trading = False
        static.settings_start = False
        static.config.save()
        static.strategy.stop()
        self.close()
if __name__ == "__main__":

    app = QApplication(sys.argv)
    GUI = SettingsWidget()
    GUI.show()
    sys.exit(app.exec_())
