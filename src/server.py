import time
import threading
import asyncio
import datetime

from pprint import pprint
import aioschedule as schedule
import pyupbit
import pandas as pd
from pymongo import MongoClient, CursorType

import config
from db import DBHandler


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
        self.request_limit = request_limit
        self.thread_status = False
        self.codes = pyupbit.get_tickers(fiat=config.FIAT)

    def start(self):
        print('DataManager sync start')
        self.thread_status = True
        self.thread = threading.Thread(
            target=self._master_thread, name='dm_master', daemon=True)
        self.thread.start()

    def stop(self):
        self.thread_status = False
        self.thread.join()
        return True

    def _get_saver_list(self):
        return [asyncio.ensure_future(self._candle_saver(code)) for code in self.codes]

    def _master_thread(self):
        print('master thread on')
        # 다음 정각 분이 될때까지 대기
        time.sleep(60 - datetime.datetime.now().second)
        # 스케줄러에 작업 등록
        schedule.every(1).minutes.do(self._slave_thread).tag('dm_slave')
        while self.thread_status:
            asyncio.run(schedule.run_pending())
            time.sleep(60 - datetime.datetime.now().second)

    async def _slave_thread(self):
        self.saver_list = self._get_saver_list()
        
        await asyncio.wait(self.saver_list, timeout=self.internal_timeout)
        # for x in range(0, len(self.saver_list), 10):
            # await asyncio.wait(self.saver_list[x:x+10], timeout=self.internal_timeout)
        
        print('saving complete')


    async def _candle_saver(self, code: str = None):
        try:
            # TODO pyupbit의 async 기반 포팅이 필요할듯
            candle_df = pyupbit.get_ohlcv(
            ticker=code, interval="minute1", count=200)
            candle_df['_id'] = [time.mktime(datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S").timetuple()) for x in candle_df['time']]
            candle_list = [candle_df.loc[i, :].to_dict() for i in range(len(candle_df) - 1)]
            # TODO asyncmongo 로 기반 모듈 전환해야함
            if self.db_handler.insert_item_many(data=candle_list, db_name='candles', collection_name=f'{code}_minute_1', ordered=False):
                self.request_status = True
                print(code, 'candle save complete')
        except Exception as e:
            pass
            # print(code, 'candle save failure', e)
        # await asyncio.sleep(self.internal_timeout)


if __name__ == '__main__':

    db = DBHandler(ip=config.DB['IP'], port=config.DB['PORT'],
                   id=config.DB['ID'], password=config.DB['PASSWORD'])
    dm = DataManager(db_handler=db)
    dm.start()
    while True:
        pprint(schedule.jobs)
        time.sleep(10)
