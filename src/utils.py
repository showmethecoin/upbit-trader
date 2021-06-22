# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import logging
import asyncio as aio
from  multiprocessing import set_start_method

def get_logger(print_format: str = '[%(asctime)s.%(msecs)03d: %(levelname).1s %(filename)s:%(lineno)s] %(message)s',
               date_format: str = '%Y-%m-%d %H:%M:%S',
               print: bool = True,
               save: bool = True,
               save_path: str = 'upbit-trader.log'):
    ''' Logger Configuration'''
    log = logging.getLogger()
    # Setup logger level
    log.setLevel(logging.INFO)
    # Setup logger format
    formatter = logging.Formatter(fmt=print_format, datefmt=date_format)
    # Setup logger handler
    if print:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        log.addHandler(stream_handler)
    if save:
        if save_path == 'upbit-trader.log' and not sys.platform.startswith('win'):
            file_handler = logging.FileHandler('upbit-trader.log')
        else:
            file_handler = logging.FileHandler(save_path)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)
    return log


def get_file_path(filename: str):
    if getattr(sys, "frozen", False):
        # The application is frozen.
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen.
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)


def set_windows_selector_event_loop_global():
    # NOTE Windows 운영체제 환경에서 Python 3.7+부터 발생하는 EventLoop RuntimeError 관련 처리
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
	    aio.set_event_loop_policy(aio.WindowsSelectorEventLoopPolicy())


def set_multiprocessing_context():
    if sys.platform == 'darwin' and getattr(sys, "frozen", False):
        set_start_method('fork')
