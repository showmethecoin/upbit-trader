# !/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio

import multiprocessing
import aiopyupbit

import utils
import static
from static import log
import component
import db
import strategy
import widget_login
import prompt


def init() -> bool:
    """초기화

    Returns:
        bool: 성공 여부
    """
    try:
        # Asyncio initialization
        utils.set_windows_selector_event_loop_global()

        # Multiprocessing initialization
        utils.set_multiprocessing_context()
        multiprocessing.freeze_support()

        # SignalManager initialization
        static.signal_queue = multiprocessing.Queue()
        static.signal_manager = strategy.SignalManager(
            queue=static.signal_queue)

        # RealtimeManager initialization
        codes = asyncio.run(aiopyupbit.get_tickers(
            fiat=static.FIAT, contain_name=True))
        static.chart = component.RealtimeManager(codes=codes)

        # DBHandler initialization
        static.db = db.DBHandler(ip=static.config.mongo_ip, port=static.config.mongo_port,
                                 id=static.config.mongo_id, password=static.config.mongo_password)

        log.info('Initialization complete')
        return True
    except:
        return False


def main() -> None:
    """프로그램 메인
    """
    static.chart.start()
    static.signal_manager.start()

    # GUI
    # widget_login.gui_main()

    # CLI
    static.upbit = aiopyupbit.Upbit(static.config.upbit_access_key,
                                    static.config.upbit_secret_key)
    prompt.prompt_main()


if __name__ == '__main__':
    init()
    main()
