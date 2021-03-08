# !/usr/bin/python
# -*- coding: utf-8 -*-
# System libraries
import os
import time
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
    
    # Prompt window size setting
    # os.system(f"mode con: lines={config.PROGRAM['HEIGHT']} cols={config.PROGRAM['WIDTH']}")

    # Upbit coin chart
    static.chart = Chart()
    static.chart.sync_start()

    # User upbit connection
    static.upbit = pyupbit.Upbit(config.KEY["ACCESS"], config.KEY["SECRET"])

    return True


def main() -> None:
    """프로그램 메인
    """

    prompt.prompt_main()


if __name__ == '__main__':
    
    log.info('Starting ' + config.PROGRAM['NAME'] + ' version ' + config.PROGRAM['VERSION'])
    
    init()
    main()
