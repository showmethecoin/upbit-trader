# !/usr/bin/python
# -*- coding: utf-8 -*-
import utils
import config as cf

''' Constant '''
MIN_TRADE_PRICE = 5000
FEES = 0.0005                           # Upbit official fees ratio
FIAT = "KRW"                            # KRW/BRC/ETH/USDT
BASE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'  # Base time format
UPBIT_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'  # Upbit time format
STRATEGY_DAILY_FINISH_TIME = 9          # Strategy finish time(24H)
EXTERNAL_TIMEOUT = 60
INTERNAL_TIMEOUT = 1
REQUEST_LIMIT = 10
PING_INTERVAL = 60

''' Variable '''
# Common
config = cf.Config()                                # Config
config.load()
log = utils.get_logger(print_format=config.log_format,  # Logger
                       print=config.log_print,
                       save=config.log_save,
                       save_path=config.log_path)
upbit = None                                            # Upbit interface
# Client
chart = None                                            # Realtime manager
account = None                                          # Account
signal_manager = None                                   # Signal manager
signal_queue = None                                     # Signal queue
strategy = None
# Server
data_manager = None                                     # Data manager
settings_start = False
