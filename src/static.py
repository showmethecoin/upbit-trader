# !/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import config

chart = None
upbit = None
db = None
data_manager = None
account = None

''' Logger Configuration'''
log = logging.getLogger()
# Setup logger level
log.setLevel(logging.INFO)
# Setup logger format
formatter = logging.Formatter(
    fmt=config.LOG['PRINT_FORMAT'], datefmt=config.TIME_FORMAT)
# Setup logger handler
if config.LOG['PRINT']:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
if config.LOG['SAVE']:
    file_handler = logging.FileHandler(config.LOG['PATH'])
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
