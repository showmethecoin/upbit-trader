import sys
import time
import asyncio
import datetime
import traceback

from apscheduler.schedulers.background import BackgroundScheduler
import pyupbit
import pandas as pd
import pymongo

import config
from db import DBHandler
import static
from static import log


# class Queue:
#     def __init__(self):
#         self._items = deque()
#         self._lock = Lock()

#     # 생산자(producer)인 디지털 카메라는 새 이미지를 대기 아이템 리스트의 끝에 추가
#     def put(self, item):
#         with self._lock:
#             self._items.append(item)

#     # 소비자(consumer)인 처리 파이프라인의 첫 번쨰 단계에서는 대기 아이템 리스트의 앞쪽에서 이미지 추출
#     def get(self):
#         with self._lock:
#             return self._items.popleft()

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
        self._db_handler = db_handler
        self._external_timeout = external_timeout
        self._internal_timeout = internal_timeout
        self._request_counter = request_limit
        self._request_limit = request_limit
        self._scheduler = BackgroundScheduler()
        self._scheduler_status = False
        self._codes = asyncio.run(pyupbit.get_tickers(fiat=config.FIAT))
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
        loop.run_until_complete(self._one_minute_candle())
        loop.close()
        log.info(f'Candle sync sequence complete')

    async def _get_sync_list(self, codes: list, base_time: str = None):
        try:
            return [asyncio.create_task(self._request_and_save(code, base_time)) for code in codes]
        except:
            print(traceback.format_exc())

    async def _one_minute_candle(self):
        """1분 캔들 데이터 동기화 서브 루프
        """
        try:
            self._lock = asyncio.Lock()
            self._request_counter = self._request_limit
            base_time = datetime.datetime.now().replace(second=0, 
                                                        microsecond=0).strftime(config.UPBIT_TIME_FORMAT)
            sync_list = await self._get_sync_list(codes=self._codes, base_time=base_time)

            while sync_list:
                overflow_requests = []
                for i in range(0, len(sync_list), self._request_limit):
                    request_result = list(filter(None, await asyncio.gather(*sync_list[i:i+self._request_limit])))
                    overflow_requests.extend(request_result)
                log.info(
                    f'Limit overflow requests({len(overflow_requests)}): {overflow_requests}')
                sync_list = await self._get_sync_list(codes=overflow_requests, 
                                                      base_time=base_time)
        except:
            print(traceback.format_exc())

    async def _request_and_save(self, code: str = None, base_time: str = None) -> None or str:
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
                    candle_df = await pyupbit.get_ohlcv(ticker=code,
                                                        interval="minute1",
                                                        count=200)
                    # TODO get_ohlcv에 to 옵션 줘서 추가할 데이터가 존재하지 않을경우 재시도 요청목록에 추가
                    break
                else:
                    async with self._lock:
                        self._request_counter = self._request_limit
                        await asyncio.sleep(self._internal_timeout)

            candle_df = candle_df[candle_df['time'] < base_time]

            candle_df['_id'] = [time.mktime(datetime.datetime.strptime(
                x, config.UPBIT_TIME_FORMAT).timetuple()) for x in candle_df['time']]

            candle_list = [candle_df.iloc[i].to_dict()
                           for i in range(len(candle_df))]
            # TODO 만약 캔들데이터가 비정상적(캔들 부족)인 경우 재요청을 위한 처리 필요
            if datetime.datetime.strptime(candle_list[-1]['time'], config.UPBIT_TIME_FORMAT) < datetime.datetime.strptime(base_time, config.UPBIT_TIME_FORMAT) - datetime.timedelta(minutes=1):
                log.warning(f'CandleTimeError\ncode    : {code}\nbase    : {base_time}\nresponse: {candle_list[-1]["time"]}')
                return code

            await self._db_handler.insert_item_many(data=candle_list,
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

    log.info(
        f'Starting {config.PROGRAM["NAME"]} Server version {config.PROGRAM["VERSION"]}')

    # NOTE Windows 운영체제 환경에서 Python 3.7+부터 발생하는 EventLoop RuntimeError 관련 처리
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
	    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    static.db = DBHandler(ip=config.DB['IP'],
                          port=config.DB['PORT'],
                          id=config.DB['ID'],
                          password=config.DB['PASSWORD'])
    static.data_manager = DataManager(db_handler=static.db)
    static.data_manager.start()

    while True:
        time.sleep(1)
