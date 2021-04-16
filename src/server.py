import time
import threading
import asyncio
import datetime
import traceback

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import pyupbit
import pandas as pd

import config
from db import DBHandler


class AsyncCounter:
    def __init__(self, start=0, end=-1, interval=1, interval_timer=1, coroutine=True):
        self.start = start
        self.end = end
        self.interval = interval
        self.interval_timer = interval_timer
        self.coroutine = coroutine

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.start < self.end:
            if self.coroutine:
                await asyncio.sleep(self.interval_timer)
            else:
                time.sleep(self.interval_timer)

            r = self.start
            self.start += self.interval
            return r
        else:
            raise StopAsyncIteration


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
        self.thread_status = False
        self.codes = asyncio.run(pyupbit.get_tickers(fiat=config.FIAT))
        self.lock = threading.Lock()

        # self.scheduler = AsyncIOScheduler(event_loop=self.loop)
        self.scheduler = BackgroundScheduler()

    def start(self):
        print('DataManager sync start')
        self.thread_status = True
        self.scheduler.add_job(self._master_thread,
                               'cron', 
                               second='0', 
                               id="dm_master")
        self.scheduler.start()

        self.thread = threading.Thread(
            target=self._counter_thread, 
            name='dm_counter', 
            daemon=True)
        self.thread.start()

    def stop(self):
        self.scheduler.shutdown()
        self.thread_status = False
        self.thread.join()
        return True

    async def _get_saver_list(self):
        return [asyncio.ensure_future(self._candle_saver(code)) for code in self.codes]

    def _master_thread(self):
        print('master thread on')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._slave_thread())
        loop.close()
        print('master_thread is terminated')

    async def _slave_thread(self):
        self.saver_list = await self._get_saver_list()
        overflow_list = []
        for i in range(0, len(self.saver_list), self.request_limit):
            result = list(filter(None, await asyncio.gather(*self.saver_list[i:i+self.request_limit], return_exceptions=False)))
            overflow_list.extend(result)
 
        print('요청 초과된 새끼 딱대 시발', overflow_list, len(overflow_list))

    async def _candle_saver(self, code: str = None):
        try:
            while True:
                if self.request_counter > 0:
                    self.lock.acquire()
                    self.request_counter -= 1
                    self.lock.release()
                    candle_df = await pyupbit.get_ohlcv(ticker=code, 
                                                        interval="minute1", 
                                                        count=2)
                    if isinstance(candle_df, type(None)):
                        return code
                    
                    break
                else:
                    await asyncio.sleep(0.1)
                    
            candle_df['_id'] = [time.mktime(datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S").timetuple()) for x in candle_df['time']]
            candle_list = [candle_df.loc[i, :].to_dict() for i in range(len(candle_df) - 1)]
            
            # TODO asyncmongo 로 기반 모듈 전환해야함
            self.db_handler.insert_item_many(data=candle_list, 
                                             db_name='candles', 
                                             collection_name=f'{code}_minute_1', 
                                             ordered=False)
            return
        except Exception as e:
            pass
            # print(traceback.format_exc())

    def _counter_thread(self):
        print('counter thread on')
        while self.thread_status:
            if self.request_counter <= 0:
                self.lock.acquire()
                self.request_counter = self.request_limit
                time.sleep(self.internal_timeout)
                self.lock.release()
            else:
                time.sleep(0.1)


if __name__ == '__main__':

    import sys
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
	    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    db = DBHandler(ip=config.DB['IP'], port=config.DB['PORT'],
                   id=config.DB['ID'], password=config.DB['PASSWORD'])
    dm = DataManager(db_handler=db)
    dm.start()
    while True:
        time.sleep(1)
