# !/usr/bin/python
# -*- coding: utf-8 -*-
KEY = { # Issued [Upbit Web]-[My Page]-[OpenAPI Management]
    "ACCESS": "CwCxiKk6m71VvffVsArkwVUHsyofxuzQ4ZyPfjaZ", # Upbit API private access key
    "SECRET": "GsVxewCvfPOzBYBqoixexRToajnJSghS9qMLoiA5" # Upbit API private secret key
}

PROGRAM = {
    "NAME": "Upbit Automatic Trading Program",
    "VERSION": "0.1",
    "WIDTH": 108, 
    "HEIGHT": 200,
}

FEES = 0.005 # Upbit official fees
FIAT = "KRW" # KRW/BRC/ETH/USDT

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG = {
    'PATH': './upbit-trader.log',
    'PRINT_FORMAT': '[%(asctime)s.%(msecs)03d: %(levelname).1s %(filename)s:%(lineno)s] %(message)s',
    'SAVE': True,
    'PRINT': False,
}