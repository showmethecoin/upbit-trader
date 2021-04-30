# !/usr/bin/python
# -*- coding: utf-8 -*-
# Issued [Upbit Web]-[My Page]-[OpenAPI Management]
KEY = {
    # Upbit API private access key
    "ACCESS": "########################################",
    # Upbit API private secret key 
    "SECRET": "########################################" 
}

PROGRAM = {
    "NAME": "Upbit Automatic Trading Program",
    "VERSION": "0.5",
    "WIDTH": 108, 
    "HEIGHT": 200,
}

DB = {
    "IP": "codejune.iptime.org",
    "PORT": 27017,
    "ID": "root",
    "PASSWORD": "qwe123"
}

SERVER = {
    "EXTERNAL_TIMEOUT": 60,
    "INTERNAL_TIMEOUT": 1,
    "REQUEST_LIMIT": 10,
}

# Upbit official fees ratio
FEES = 0.005 
# KRW/BRC/ETH/USDT
FIAT = "KRW" 

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
UPBIT_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

LOG = {
    'PATH': './upbit-trader.log',
    'PRINT_FORMAT': '[%(asctime)s.%(msecs)03d: %(levelname).1s %(filename)s:%(lineno)s] %(message)s',
    'SAVE': True,
    'PRINT': True,
}