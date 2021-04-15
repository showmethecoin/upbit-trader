import time
import threading
import asyncio
import datetime

import aioschedule as schedule
import pyupbit
import pandas as pd
from pymongo import MongoClient, CursorType

from db import DBHandler
import config


class DataManager:
    def __init__(self,
                 db_handler: DBHandler = None,
                 external_timeout: int = config.SERVER["EXTERNAL_TIMEOUT"], 
                 internal_timeout: int = config.SERVER["INTERNAL_TIMEOUT"], 
                 request_limit: int = config.SERVER["REQUEST_LIMIT"]):
        self.db_handler = db_handler
        self.external_timeout = external_timeout
        self.internal_timeout = internal_timeout
        self.request_limit = request_limit
        self.saver_list = []
        self.thread_status = False

        for i in pyupbit.get_tickers(fiat=config.FIAT):
            self.saver_list.append(CandleSaver(code=i, db_handler=self.db_handler).start)

    def start(self, loop):
        print('DataManager sync start')
        self.thread_status = True
        self.thread = threading.Thread(target=self._master_thread, daemon=True, args=(loop,))
        self.thread.start()
    
    def _master_thread(self, loop):
        print('master thread on')
        schedule.every().minutes.do(self._slave_thread)
        while self.thread_status:
            loop.run_until_complete(schedule.run_pending())
            time.sleep(1)
                
    async def _slave_thread(self):
        print('slave thread on')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for x in range(0, len(self.saver_list), 10):
            loop.run_until_complete(asyncio.wait(self.saver_list[x:x+10], timeout=self.internal_timeout))


class CandleSaver:
    """코인 캔들 데이터 저장 클래스
    """

    def __init__(self, 
                 code: str = None,
                 db_handler: DBHandler = None):
        """생성자
        Args:
            external_timeout (int, optional): 전체 요청 타임아웃 시간. Defaults to config.SERVER["EXTERNAL_TIMEOUT"].
            internal_timeout (int, optional): 개별 요청 타임아웃 시간. Defaults to config.SERVER["INTERNAL_TIMEOUT"].
            request_limit (int, optional): 코인 개별 요청 최대 개수. Defaults to config.SERVER["REQUEST_LIMIT"].
        """
        self.code = code
        self.db_handler = db_handler
        self.request_status = False
        
    async def start(self):
        print(self.code, 'candle start')
        try:
            candle_df = pyupbit.get_ohlcv(ticker=self.code, interval="minute1", count=200)
            candle_list = [candle_df.loc[i, :].to_dict() for i in range(len(candle_df) - 1)]
            if db.insert_item_many(data=candle_list, db_name='candles', collection_name=f'{self.code}_minute_1'):
                self.request_status = True
        except:
            pass
        time.sleep(1)

if __name__ == '__main__':

    db = DBHandler(ip=config.DB['IP'], port=config.DB['PORT'],
                   id=config.DB['ID'], password=config.DB['PASSWORD'])
    dm = DataManager(db_handler=db)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    dm.start(loop)
    while True:
        time.sleep(1)
