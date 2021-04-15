import time
import threading
import datetime

import pyupbit
import pandas as pd
from pymongo import MongoClient, CursorType

from db import DBHandler
import config


class Server:
    def __init__(self):
        pass


class CandleSaver:
    """코인 캔들 데이터 저장 클래스
    """

    def __init__(self, 
                 external_timeout: int = config.SERVER["EXTERNAL_TIMEOUT"], 
                 internal_timeout: int = config.SERVER["INTERNAL_TIMEOUT"], 
                 request_limit: int = config.SERVER["REQUEST_LIMIT"]):
        """생성자
        Args:
            external_timeout (int, optional): 전체 요청 타임아웃 시간. Defaults to config.SERVER["EXTERNAL_TIMEOUT"].
            internal_timeout (int, optional): 개별 요청 타임아웃 시간. Defaults to config.SERVER["INTERNAL_TIMEOUT"].
            request_limit (int, optional): 코인 개별 요청 최대 개수. Defaults to config.SERVER["REQUEST_LIMIT"].
        """
        self.external_timeout = external_timeout
        self.internal_timeout = internal_timeout
        self.request_limit = request_limit
        self.tickers = pyupbit.get_tickers(fiat=config.FIAT)

    def start(self):
        start = time.time()
        #
        # 여기에 작업할 내용 추가하기
        #
        print("time :", time.time() - start)
        timer = threading.Timer(self.external_timeout, self.start)
        timer.start()


if __name__ == '__main__':

    cs = CandleSaver()
    print(len(cs.tickers))

    db = DBHandler(ip=config.DB['IP'], port=config.DB['PORT'],
                   id=config.DB['ID'], password=config.DB['PASSWORD'])
    while True:
        items_df = pyupbit.get_ohlcv(
            ticker="KRW-BTC", interval="minute1", count=200)
        
        """ 리샘플링 코드 시작 """
        items_df['time'] = pd.to_datetime(items_df['time'])
        items_df = items_df.set_index('time', inplace=False)
        print(items_df)

        new_df = pd.DataFrame()
        new_df['open'] = items_df.open.resample('15T').first()
        new_df['high'] = items_df.high.resample('15T').max()
        new_df['low'] = items_df.low.resample('15T').min()
        new_df['close'] = items_df.close.resample('15T').last()
        new_df['volume'] = items_df.volume.resample('15T').sum()
        print(new_df)
        """ 리샘플링 코드 끝 """

        items = [items_df.loc[i, :].to_dict() for i in range(len(items_df))]
        for i in items:
            query = {'time': {'$in': [i['time']]}}
            ret = db.find_item_one(
                condition=query, db_name='history', collection_name='KRW_BTC_1_minute')
            if ret != None:
                pass
                # print(ret)
            else:
                print(db.insert_item_one(
                    data=i, db_name='history', collection_name='KRW_BTC_1minute'))

        time.sleep(1)
