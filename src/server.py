# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import asyncio as aio
import multiprocessing as mp
import datetime
import traceback

from apscheduler.schedulers.background import BackgroundScheduler
import pymongo
import aiopyupbit
import pandas as pd

import utils
import config
import static
from static import log
from db import DBHandler


class SaveManager(mp.Process):
    def __init__(self,
                 db_ip: str,
                 db_port: int,
                 db_id: str,
                 db_password: str,
                 save_queue: mp.Queue):
        # Public
        self.alive = False
        self.db_ip = db_ip
        self.db_port = db_port
        self.db_id = db_id
        self.db_password = db_password
        # Private
        self.__save_queue = save_queue

        super().__init__()

    def run(self) -> None:
        log.info('Start save manager process')
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        loop.run_until_complete(self.__save_loop())

    def terminate(self) -> None:
        log.info('Stop save manager process')
        self.alive = False
        return super().terminate()

    async def __save_loop(self):
        db = DBHandler(ip=self.db_ip,
                       port=self.db_port,
                       id=self.db_id,
                       password=self.db_password)
        while self.alive:
            try:
                data = self.__save_queue.get()
                await db.insert_item_many(data=data['data'],
                                          db_name=data['db_name'],
                                          collection_name=data['collection_name'],
                                          ordered=data['ordered'])
            # Mongo DB에 중복 데이터 저장 시도시 발생하는 에러 처리
            except pymongo.errors.BulkWriteError:
                pass


class RequestManager(mp.Process):
    def __init__(self,
                 in_queue: mp.Queue,
                 out_queue: mp.Queue,
                 save_queue: mp.Queue):
        # Public
        self.alive = False
        # Private
        self.__in_queue = in_queue
        self.__out_queue = out_queue
        self.__save_queue = save_queue

        super().__init__()

    def run(self) -> None:
        log.info('Start request manager process')
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        loop.run_until_complete(self.__request_loop())

    def terminate(self) -> None:
        log.info('Stop request manager process')
        self.alive = False
        return super().terminate()

    async def __get_sync_list(self, codes: list, base_time: str):
        try:
            return [aio.create_task(self.__request(code, base_time)) for code in codes]
        except:
            print(traceback.format_exc())

    async def __request_loop(self):
        while self.alive:
            data = self.__in_queue.get()
            request_list = await self.__get_sync_list(codes=data['codes'],
                                                      base_time=data['base_time'])
            request_result = list(filter(None, await aio.gather(*request_list)))
            self.__out_queue.put(request_result)

    async def __request(self, code: str, base_time: str) -> None or str:
        try:
            candle_df = await aiopyupbit.get_ohlcv(ticker=code,
                                                   interval="minute1",
                                                   count=200)

            candle_df = candle_df[candle_df['time'] < base_time]
            candle_df['_id'] = [time.mktime(datetime.datetime.strptime(
                x, static.UPBIT_TIME_FORMAT).timetuple()) for x in candle_df['time']]
            candle_list = [candle_df.iloc[i].to_dict()
                           for i in range(len(candle_df))]

            # TODO 만약 캔들데이터가 비정상적(캔들 부족)인 경우 재요청을 위한 처리 필요
            if datetime.datetime.strptime(candle_list[-1]['time'], static.UPBIT_TIME_FORMAT) < datetime.datetime.strptime(base_time, static.UPBIT_TIME_FORMAT) - datetime.timedelta(minutes=1):
                log.warning(
                    f'CandleTimeError\ncode    : {code}\nbase    : {base_time}\nresponse: {candle_list[-1]["time"]}')
                return code

            data = {'data': candle_list,
                    'db_name': 'candles',
                    'collection_name': f'{code}_minute_1',
                    'ordered': False}
            self.__save_queue.put(data)
            return
        except TypeError:
            # 요청 횟수 제한 초과시 재시도 요청 목록에 포함시키기 위해 코인 마켓 코드 반환
            return code
        except:
            print(traceback.format_exc())
            return code


class DataManager:
    def __init__(self,
                 db_ip: str,
                 db_port: int,
                 db_id: str,
                 db_password: str,
                 external_timeout: int = 60,
                 internal_timeout: int = 1,
                 request_limit: int = 10):
        # Public
        self.db_ip = db_ip
        self.db_port = db_port
        self.db_id = db_id
        self.db_password = db_password
        self.external_timeout = external_timeout
        self.internal_timeout = internal_timeout
        self.request_limit = request_limit
        self.alive = False
        # Private
        self.__loop = aio.new_event_loop()
        aio.set_event_loop(self.__loop)
        self.__db = DBHandler(ip=self.db_ip,
                              port=self.db_port,
                              id=self.db_id,
                              password=self.db_password,
                              loop=self.__loop)
        self.__codes = self.__loop.run_until_complete(
            aiopyupbit.get_tickers(fiat=static.FIAT))
        self.__scheduler = BackgroundScheduler()
        self.__request_in_queue = mp.Queue()
        self.__request_out_queue = mp.Queue()
        self.__save_queue = mp.Queue()

    def start(self) -> None:
        """스케줄러 시작
        """
        self.alive = True
        self.__scheduler.add_job(func=self._one_minute_sync_loop,
                                 trigger='cron',
                                 second='0',
                                 id="data_manager_one_minute_sync_loop")
        self.__scheduler.start()
        self.__save_manager = SaveManager(db_ip=self.db_ip,
                                          db_port=self.db_port,
                                          db_id=self.db_id,
                                          db_password=self.db_password,
                                          save_queue=self.__save_queue)
        self.__request_manager = RequestManager(in_queue=self.__request_in_queue,
                                                out_queue=self.__request_out_queue,
                                                save_queue=self.__save_queue)
        self.__request_manager.start()
        self.__save_manager.start()

    def stop(self) -> None:
        """스케줄러 종료
        """
        self.alive = False
        self.__scheduler.shutdown()
        self.__request_manager.terminate()
        self.__save_manager.terminate()

    def _one_minute_sync_loop(self):
        """캔들 데이터 동기화 메인 루프
        """
        log.info(f'One minute candles sync sequence start')
        try:
            base_time = datetime.datetime.now().replace(
                second=0, microsecond=0).strftime(static.UPBIT_TIME_FORMAT)
            sync_list = self.__codes
            while sync_list:
                overflow_requests = []
                for i in range(0, len(sync_list), self.request_limit):
                    data = {
                        'base_time': base_time,
                        'codes': sync_list[i:i+self.request_limit]}
                    start = time.time()
                    self.__request_in_queue.put(data)
                    request_result = self.__request_out_queue.get()
                    spend_time = time.time() - start
                    log.info(f'Request spend time: {spend_time}')
                    if spend_time < 1:
                        time.sleep(1 - spend_time)
                    overflow_requests.extend(request_result)

                log.info(
                    f'Limit overflow requests({len(overflow_requests)}): {overflow_requests}')
                sync_list = overflow_requests

            if self.__request_out_queue.empty():
                log.info(f'Candle sync sequence complete')
            else:
                log.info(f'Candle sync sequence failed')
        except:
            print(traceback.format_exc())

    def _other_sync_loop(self, target: str):
        """캔들 데이터 동기화 메인 루프
        """
        self.__loop.run_until_complete(self._other_sync(target=target))

    async def _other_sync(self, target: str):
        for code in self.codes:
            data = await self.__db.find_item(condition=None, db_name='candles',
                                             collection_name=f'{code}_minute_1')
            data_df = pd.DataFrame(await data.to_list(length=None))
            # Dataframe 인덱스 설정
            data_df['time'] = pd.to_datetime(data_df['time'])
            data_df = data_df.set_index('time', inplace=False)

            # Dataframe 리샘플링
            if target == 'minute_3':
                RESAMPLING = '3T'
            elif target == 'minute_5':
                RESAMPLING = '5T'
            elif target == 'minute_10':
                RESAMPLING = '10T'
            elif target == 'minute_15':
                RESAMPLING = '15T'
            elif target == 'minute_30':
                RESAMPLING = '30T'
            elif target == 'minute_60':
                RESAMPLING = '1H'
            elif target == 'minute_240':
                RESAMPLING = '4H'
            elif target == 'day':
                RESAMPLING = '1D'
            elif target == 'week':
                RESAMPLING = 'B'
            elif target == 'month':
                RESAMPLING = '1M'

            new_df = pd.DataFrame()
            if not 'minute' in target:
                new_df['open'] = data_df.open.resample(RESAMPLING).first()
                new_df['high'] = data_df.high.resample(RESAMPLING).max()
                new_df['low'] = data_df.low.resample(RESAMPLING).min()
                new_df['close'] = data_df.close.resample(RESAMPLING).last()
                new_df['volume'] = data_df.volume.resample(RESAMPLING).sum()
            else:
                new_df['open'] = data_df.open.resample(RESAMPLING).first()
                new_df['high'] = data_df.high.resample(RESAMPLING).max()
                new_df['low'] = data_df.low.resample(RESAMPLING).min()
                new_df['close'] = data_df.close.resample(RESAMPLING).last()
                new_df['volume'] = data_df.volume.resample(RESAMPLING).sum()
            new_df = new_df.sort_index(ascending=True)


if __name__ == '__main__':

    utils.set_windows_selector_event_loop_global()

    static.config = config.Config()
    static.config.load()
    static.data_manager = DataManager(db_ip=static.config.mongo_ip,
                                      db_port=static.config.mongo_port,
                                      db_id=static.config.mongo_id,
                                      db_password=static.config.mongo_password,
                                      external_timeout=static.EXTERNAL_TIMEOUT,
                                      internal_timeout=static.INTERNAL_TIMEOUT,
                                      request_limit=static.REQUEST_LIMIT)
    static.data_manager.start()

    while True:
        time.sleep(1)
