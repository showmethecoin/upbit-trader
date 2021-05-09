# !/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import asyncio

import config
import static
import component
from static import log
from widget_login import gui_main
import aiopyupbit


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

    # Upbit coin chart
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    codes = loop.run_until_complete(aiopyupbit.get_tickers(fiat=config.FIAT, contain_name=True))
    static.chart = component.RealtimeManager(codes=codes)
    static.chart.start()


    # Prompt window size setting
    # os.system(f"mode con: lines={config.PROGRAM['HEIGHT']} cols={config.PROGRAM['WIDTH']}")

    return True


def main() -> None:
    """프로그램 메인
    """

    gui_main()
    #prompt.prompt_main()


if __name__ == '__main__':

    log.info(
        f'Starting {config.PROGRAM["NAME"]} version {config.PROGRAM["VERSION"]}')

    init()
    main()
