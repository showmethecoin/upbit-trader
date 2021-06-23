# !/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio as aio

from multiprocessing import Queue, freeze_support
import aiopyupbit

import static
from static import log
from utils import set_windows_selector_event_loop_global, set_multiprocessing_context
from component import RealtimeManager, Account
from strategy import SignalManager
from widget_login import gui_main
from prompt import prompt_main


def init() -> bool:
    """초기화

    Returns:
        bool: 성공 여부
    """
    try:
        # Asyncio initialization
        set_windows_selector_event_loop_global()

        # Multiprocessing initialization
        set_multiprocessing_context()
        freeze_support()

        # SignalManager initialization
        static.signal_queue = Queue()

        # RealtimeManager initialization
        codes = aio.run(aiopyupbit.get_tickers(fiat=static.FIAT,
                                               contain_name=True))
        static.chart = RealtimeManager(codes=codes)

        log.info('Initialization complete')
        return True
    except:
        import traceback
        print(traceback.format_exc())
        return False


def main(gui: bool = True) -> None:
    """프로그램 메인
    """

    static.chart.start()
    if gui:
        # GUI
        gui_main()
    else:
        # Account initialization
        static.signal_manager = SignalManager(config=static.config,
                                              db_ip=static.config.mongo_ip,
                                              db_port=static.config.mongo_port,
                                              db_id=static.config.mongo_id,
                                              db_password=static.config.mongo_password,
                                              queue=static.signal_queue)
        static.signal_manager.start()
        static.account = Account(access_key=static.config.upbit_access_key,
                                 secret_key=static.config.upbit_secret_key)
        static.account.start()
        # CLI
        prompt_main()


if __name__ == '__main__':
    if init():
        main(gui=static.config.gui)
