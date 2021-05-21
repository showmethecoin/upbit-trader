# !/usr/bin/python
# -*- coding: utf-8 -*-
import utils

FEES = 0.0005  # Upbit official fees ratio
FIAT = "KRW"  # KRW/BRC/ETH/USDT
BASE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'  # Base time format
UPBIT_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S' # Upbit time format
EXTERNAL_TIMEOUT = 60
INTERNAL_TIMEOUT = 1
REQUEST_LIMIT = 10
PING_INTERVAL = 60

log = utils.get_logger()
chart = None
upbit = None
db = None
data_manager = None
account = None
config = None
