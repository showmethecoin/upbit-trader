# !/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio

import aiopyupbit

import utils
import config
import static
from static import log
import component
import widget_login


def init() -> bool:
    """초기화

    Returns:
        bool: 성공 여부
    """

    log.info('Initializing...')
    
    utils.set_windows_selector_event_loop_global()
    utils.set_multiprocessing_context()
    
    static.config = config.Config()
    static.config.load()
    
    # Upbit coin chart
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=static.FIAT, contain_name=True))
    static.chart = component.RealtimeManager(codes=codes)
    static.chart.start()

    # Prompt window size setting
    # os.system(f"mode con: lines={config.PROGRAM['HEIGHT']} cols={config.PROGRAM['WIDTH']}")

    return True


def main() -> None:
    """프로그램 메인
    """

    widget_login.gui_main()
    #prompt.prompt_main()


if __name__ == '__main__':

    init()
    main()
