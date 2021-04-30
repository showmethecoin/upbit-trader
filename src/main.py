# !/usr/bin/python
# -*- coding: utf-8 -*-
# System libraries
import sys
import os
import time
import asyncio
# Upbit API libraries
import pyupbit
from pyupbit.exchange_api import Upbit
# User defined modules
import config
import static
from static import log
import prompt
from component import Chart


def init() -> bool:
    """초기화

    Returns:
        bool: 성공 여부
    """

    log.info('Initializing...')
    
    # NOTE Windows 운영체제 환경에서 Python 3.7+부터 발생하는 EventLoop RuntimeError 관련 처리
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
	    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
     
    # Prompt window size setting
    # os.system(f"mode con: lines={config.PROGRAM['HEIGHT']} cols={config.PROGRAM['WIDTH']}")

    # Upbit coin chart
    static.chart = Chart()
    static.chart.sync_start()

    # User upbit connection
    static.upbit = pyupbit.Upbit(config.UPBIT["ACCESS_KEY"], config.UPBIT["SECRET_KEY"])

    return True


def main() -> None:
    """프로그램 메인
    """

    prompt.prompt_main()


if __name__ == '__main__':
    
    log.info(f'Starting {config.PROGRAM["NAME"]} version {config.PROGRAM["VERSION"]}')
    
    init()
    main()
