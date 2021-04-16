import sys
import time
import asyncio
import datetime
import traceback

from apscheduler.schedulers.background import BackgroundScheduler
import pyupbit
import pandas as pd

import config
from db import DBHandler
import static
from static import log

class DataManager:
    def __init__(self,
                 db_handler: DBHandler = None,
                 external_timeout: int = config.SERVER["EXTERNAL_TIMEOUT"],
                 internal_timeout: int = config.SERVER["INTERNAL_TIMEOUT"],
                 request_limit: int = config.SERVER["REQUEST_LIMIT"]):
        """DataManager 생성자

        Args:
            db_handler (DBHandler, optional): MongoDB 핸들러. Defaults to None.
            external_timeout (int, optional): 최대 요청 시간. Defaults to config.SERVER["EXTERNAL_TIMEOUT"].
            internal_timeout (int, optional): 최소 요청 시간. Defaults to config.SERVER["INTERNAL_TIMEOUT"].
            request_limit (int, optional): 초당 최대 요청 개수. Defaults to config.SERVER["REQUEST_LIMIT"].
        """
        self.db_handler = db_handler
        self.external_timeout = external_timeout
        self.internal_timeout = internal_timeout
        self.request_counter = request_limit
        self.request_limit = request_limit
        self.schedule_status = False
        self.codes = asyncio.run(pyupbit.get_tickers(fiat=config.FIAT))
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.schedule_status = True
        self.scheduler.add_job(func=self._master_thread,
                               trigger='cron',
                               second='0',
                               id="dm_master")
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()
        self.schedule_status = False
        self.thread.join()
        return True

    async def _get_saver_list(self, codes: list):
        return [asyncio.ensure_future(self._candle_saver(code)) for code in codes]

    def _master_thread(self):
        log.info(f'Candle sync sequence')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._slave_thread())
        loop.close()

    async def _slave_thread(self):
        self.request_counter = self.request_limit
        self.saver_list = await self._get_saver_list(self.codes)
        overflow_list = []
        self.lock = asyncio.Lock()
        try:
            for i in range(0, len(self.saver_list), self.request_limit):
                result = list(filter(None, await asyncio.gather(*self.saver_list[i:i+self.request_limit], return_exceptions=False)))
                overflow_list.extend(result)
            
            log.warning(f'Limit overflow requests({len(overflow_list)}): {overflow_list}')

            while overflow_list:
                log.warning(f'Remain overflow requests({len(overflow_list)}): {overflow_list}')
                remain_saver = await self._get_saver_list(overflow_list)
                remain_list = []
                for i in range(0, len(remain_saver), self.request_limit):
                    result = list(filter(None, await asyncio.gather(*remain_saver[i:i+self.request_limit], return_exceptions=False)))
                    remain_list.extend(result)
                overflow_list = remain_list

        except:
            print(traceback.format_exc())

    async def _candle_saver(self, code: str = None):
        try:
            while True:
                if self.request_counter > 0:
                    async with self.lock:
                        self.request_counter -= 1
                    candle_df = await pyupbit.get_ohlcv(ticker=code,
                                                        interval="minute1",
                                                        count=200)
                    if isinstance(candle_df, type(None)):
                        return code

                    break
                else:
                    async with self.lock:
                        self.request_counter = self.request_limit
                        await asyncio.sleep(0.5)

            candle_df['_id'] = [time.mktime(datetime.datetime.strptime(
                x, "%Y-%m-%dT%H:%M:%S").timetuple()) for x in candle_df['time']]
            candle_list = [candle_df.loc[i, :].to_dict()
                           for i in range(len(candle_df) - 1)]

            # TODO asyncmongo 로 기반 모듈 전환해야함
            self.db_handler.insert_item_many(data=candle_list,
                                             db_name='candles',
                                             collection_name=f'{code}_minute_1',
                                             ordered=False)
            return
        except Exception as e:
            pass
            # print(traceback.format_exc())


if __name__ == '__main__':

    log.info(f'Starting {config.PROGRAM["NAME"]} Server version {config.PROGRAM["VERSION"]}')

    # NOTE Windows 운영체제 환경에서 Python 3.7+부터 발생하는 EventLoop RuntimeError 관련 처리
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
	    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
     
    static.db = DBHandler(ip=config.DB['IP'], port=config.DB['PORT'],
                   id=config.DB['ID'], password=config.DB['PASSWORD'])
    static.data_manager = DataManager(db_handler=static.db)
    static.data_manager.start()
    
    while True:
        time.sleep(1)
