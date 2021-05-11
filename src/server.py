# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import asyncio
import datetime
import traceback

from apscheduler.schedulers.background import BackgroundScheduler
import pymongo
import aiopyupbit

import utils
import config
import static
from static import log
from db import DBHandler


class DataManager:
    def __init__(self,
                 db_ip: str = 'localhost',
                 db_port: int = 27017,
                 db_id: str = None,
                 db_password: str = None,
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
        # Protected
        self._request_counter = request_limit
        self._scheduler = BackgroundScheduler()
        self._scheduler_status = False
        self._codes = asyncio.run(aiopyupbit.get_tickers(fiat=static.FIAT))
        self._lock = None

    def start(self) -> None:
        """스케줄러 시작
        """
        self._schedule_status = True
        self._scheduler.add_job(func=self._sync_loop,
                                trigger='cron',
                                second='0',
                                id="data_manager_sync_loop")
        self._scheduler.start()

    def stop(self) -> None:
        """스케줄러 종료
        """
        self._scheduler.shutdown()
        self._scheduler_status = False

    def _sync_loop(self):
        """캔들 데이터 동기화 메인 루프
        """
        log.info(f'Candle sync sequence start')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        db = DBHandler(ip=self.db_ip,
                       port=self.db_port,
                       id=self.db_id,
                       password=self.db_password,
                       loop=loop)
        loop.run_until_complete(self._one_minute_candle(db))
        loop.close()
        log.info(f'Candle sync sequence complete')

    async def _get_sync_list(self, codes: list, base_time: str, db: DBHandler):
        try:
            return [asyncio.create_task(self._request_and_save(code, base_time, db)) for code in codes]
        except:
            print(traceback.format_exc())

    async def _one_minute_candle(self, db: DBHandler):
        """1분 캔들 데이터 동기화 서브 루프
        """
        try:
            self._lock = asyncio.Lock()
            self._request_counter = static.REQUEST_LIMIT
            base_time = datetime.datetime.now().replace(
                second=0, microsecond=0).strftime(static.UPBIT_TIME_FORMAT)
            sync_list = await self._get_sync_list(codes=self._codes,
                                                  base_time=base_time,
                                                  db=db)

            while sync_list:
                overflow_requests = []
                for i in range(0, len(sync_list), self.request_limit):
                    request_result = list(filter(None, await asyncio.gather(*sync_list[i:i+self.request_limit])))
                    overflow_requests.extend(request_result)
                log.info(
                    f'Limit overflow requests({len(overflow_requests)}): {overflow_requests}')
                sync_list = await self._get_sync_list(codes=overflow_requests,
                                                      base_time=base_time,
                                                      db=db)
        except:
            print(traceback.format_exc())

    async def _request_and_save(self, code: str = None, base_time: str = None, db: DBHandler = None) -> None or str:
        """캔들 데이터 REST 요청 및 DB 저장

        Args:
            code (str, optional): 코인 마켓 코드. Defaults to None.

        Returns:
            None or str: 요청 성공시 None, 요청 초과 및 실패시 코인 마켓 코드
        """
        try:
            while True:
                if self._request_counter > 0:
                    async with self._lock:
                        self._request_counter -= 1
                    candle_df = await aiopyupbit.get_ohlcv(ticker=code,
                                                           interval="minute1",
                                                           count=200)
                    # TODO get_ohlcv에 to 옵션 줘서 추가할 데이터가 존재하지 않을경우 재시도 요청목록에 추가
                    break
                else:
                    async with self._lock:
                        self._request_counter = self.request_limit
                        await asyncio.sleep(self.internal_timeout)

            candle_df = candle_df[candle_df['time'] < base_time]

            candle_df['_id'] = [time.mktime(datetime.datetime.strptime(
                x, static.UPBIT_TIME_FORMAT).timetuple()) for x in candle_df['time']]

            candle_list = [candle_df.iloc[i].to_dict()
                           for i in range(len(candle_df))]
            # TODO 만약 캔들데이터가 비정상적(캔들 부족)인 경우 재요청을 위한 처리 필요
            if datetime.datetime.strptime(candle_list[-1]['time'], static.UPBIT_TIME_FORMAT) < datetime.datetime.strptime(base_time, static.UPBIT_TIME_FORMAT) - datetime.timedelta(minutes=1):
                log.warning(
                    f'CandleTimeError\ncode    : {code}\nbase    : {base_time}\nresponse: {candle_list[-1]["time"]}')
                # return code

            await db.insert_item_many(data=candle_list,
                                      db_name='candles',
                                      collection_name=f'{code}_minute_1',
                                      ordered=False)
            return

        # 요청 횟수 제한 초과시 재시도 요청 목록에 포함시키기 위해 코인 마켓 코드 반환
        except TypeError:
            return code
        # Mongo DB에 중복 데이터 저장 시도시 발생하는 에러 처리
        except pymongo.errors.BulkWriteError:
            pass
        except:
            print(traceback.format_exc())
            return code


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
