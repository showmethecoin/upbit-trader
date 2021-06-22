# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime
import uuid
import asyncio as aio
from multiprocessing import Queue, Process
from threading import Thread

import numpy as np
import aiopyupbit
from pandas.core.frame import DataFrame
import talib

from component import Coin
from db import DBHandler
import static
from static import log
from config import Config


class SignalManager(Process):
    def __init__(self, config: Config, db_ip: str, db_port: int,
                 db_id: str, db_password: str, queue: Queue) -> None:
        # Public
        self.alive = False
        # Private
        self.__config = config
        self.__upbit = aiopyupbit.Upbit(access=self.__config.upbit_access_key,
                                        secret=self.__config.upbit_secret_key)
        self.__queue = queue
        self.__db_ip = db_ip
        self.__db_port = db_port
        self.__db_id = db_id
        self.__db_password = db_password
        self.__max_individual_trade_price = self.__config.max_individual_trade_price

        super().__init__()

    def run(self) -> None:
        """SignalManager 시작
        """
        log.info('Start signal manager process')
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        db = DBHandler(ip=self.__db_ip,
                       port=self.__db_port,
                       id=self.__db_id,
                       password=self.__db_password,
                       loop=loop)
        loop.run_until_complete(self.__loop(db))

    def terminate(self) -> None:
        """SignalManager 종료
        """
        log.info('Stop signal manager process')
        self.alive = False
        return super().terminate()

    async def __loop(self, db: DBHandler) -> None:
        while self.alive:
            try:
                message = self.__queue.get()
                now = datetime.datetime.now()
                message['_id'] = f'{uuid.uuid4()}'
                message['time'] = now.strftime(static.BASE_TIME_FORMAT)
                log.info(f'Signal information:\n'
                         f'_id: {message["_id"]}\n'
                         f'time: {message["time"]}\n'
                         f'code: {message["code"]}\n'
                         f'type: {message["type"]}\n'
                         f'position: {message["position"]}\n'
                         f'price: {message["price"]}')
                await db.insert_item_one(data=message, db_name='signal_history',
                                         collection_name=datetime.datetime.today().strftime("%Y-%m-%d"))

                code = message['code'].split('-')[1]
                order_list = await self.__upbit.get_order(message['code'])
                own_dict = {x['currency']: x for x in await self.__upbit.get_balances()}

                # Bid
                if message['position'] == 'bid':

                    # 보유중 확인
                    if code in own_dict.keys():
                        log.warning(f'{code} is already bought')
                        continue
                    # 주문 목록 확인
                    elif order_list:
                        log.warning(f'order_list: {order_list}')
                        # 기존 주문 취소
                        uuid_list = [x['uuid'] for x in order_list]
                        for x in uuid_list:
                            await self.__upbit.cancel_order(x)
                    # 시장가 매수
                    if message['type'] == 'market':
                        response = await self.__upbit.buy_market_order(ticker=message['code'],
                                                                       price=self.__max_individual_trade_price)
                    # 지정가 매수
                    else:
                        volume = self.__max_individual_trade_price / \
                            message['price']
                        response = await self.__upbit.buy_limit_order(ticker=message['code'],
                                                                      price=message['price'],
                                                                      volume=volume)
                # Ask
                else:
                    # 보유중 확인
                    if not code in own_dict.keys():
                        log.warning(f'{code} is not bought')
                        continue
                    # 주문 목록 확인
                    elif order_list:
                        log.warning(f'order_list: {order_list}')
                        # 기존 주문 취소
                        uuid_list = [x['uuid'] for x in order_list]
                        for x in uuid_list:
                            await self.__upbit.cancel_order(x)
                    # 시장가 매도
                    if message['type'] == 'market':
                        response = await self.__upbit.sell_market_order(ticker=message['code'],
                                                                        price=own_dict[code]['balance'])
                    # 지정가 매도
                    else:
                        response = await self.__upbit.sell_limit_order(ticker=message['code'],
                                                                       price=message['price'],
                                                                       volume=own_dict[code]['balance'])
                response_uuid_list = [x['uuid'] for x in response]
                trade_list = [{'uuid': x for x in response_uuid_list}]
                trade_list = [x.update({'signal_id': message['_id']}) for x in trade_list]
                await db.insert_item_many(data=message, db_name='signal_trade_history',
                                          collection_name=datetime.datetime.today().strftime("%Y-%m-%d"))

            except Exception as e:
                log.error(e)


class Strategy(Thread):
    def __init__(self, queue: Queue) -> None:
        super().__init__()
        # Public
        self.alive = False
        self.daemon = False
        # Private
        self.__queue = queue

    def run(self) -> None:
        """Strategy 모니터링 시작
        """
        log.info('Start strategy thread')
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        loop.run_until_complete(self.__loop())

    def terminate(self) -> None:
        """Strategy 모니터링 종료
        """
        log.info('Stop strategy thread')
        self.alive = False
        return super().terminate()

    def send_signal(self, code: str, position: str, type: str, price: float) -> None:
        """Ask/Bid signal sender function

        Args:
            code (str): Coin's code
            type (str): Signal type
            price (float): Coin's target price
        """
        self.__queue.put({'code': code, 'position': position,
                          'type': type, 'price': price})

    def get_average(self, df: DataFrame, unit: int = 5, column: str = 'close') -> float:
        """unit 동안의 평균값을 리턴하는 함수
        Args:
            df (DataFrame): 캔들봉 정보가 담긴 DataFrame
            unit (int): 평균을 구할 기간
            column (str): 평균을 구할 column
        Returns:
            (float): 해당 column의 평균값을 리턴
        """
        return df[column].rolling(unit).mean()

    async def __loop(self) -> None:
        raise NotImplementedError


class VolatilityBreakoutStrategy(Strategy):
    def __init__(self, queue: Queue, period: str = 'day') -> None:
        super().__init__(queue=queue)
        # 투자 대상 Coin 인스턴스 목록
        self.period = period

    def run(self) -> None:
        """Strategy 모니터링 시작
        """
        log.info('Start volatility breakout strategy thread')
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        loop.run_until_complete(self.__loop())

    def terminate(self) -> None:
        """Strategy 모니터링 종료
        """
        log.info('Stop volatility breakout strategy thread')
        self.alive = False
        return super().terminate()

    async def get_best_coin_list(self):
        log.info('Find best target coins, it will spend 60 sec...')
        while True:
            candidate_list = []
            for coin in static.chart.codes:
                df = await aiopyupbit.get_ohlcv(coin, interval=self.period, count=20)
                avg_5 = self.get_average(df, unit=5, column='close')[0]
                avg_10 = self.get_average(df, unit=10, column='close')[0]
                avg_20 = self.get_average(df, unit=20, column='close')[0]

                if (avg_5 > avg_10) and (avg_10 > avg_20):
                    candidate_list.append(coin)
                time.sleep(0.2)

            if candidate_list:
                break

            log.info('Cannot find best target coins, it will re-working again...')

        return [x for x in static.chart.coins.values() if x.code in candidate_list]

    async def get_best_k(self, code: str):
        """백테스팅을 통해 최적의 k를 찾는 함수
        Args:
            coin (str): k를 얻을 종목 코드
        Returns:
            백테스팅을 통해 찾은 최적의 k
        """
        # TODO 요청개수 초과 예외처리 필요함
        df = await aiopyupbit.get_ohlcv(code, interval=self.period, count=21)
        time.sleep(0.5)
        df = df.iloc[:-1]
        df['noise'] = 1 - abs(df['open'] - df['close']) / \
            (df['high'] - df['low'])
        return df['noise'].mean()

    async def get_target_price(self, coin: str, k: float):
        """목표가격을 얻는 함수
        Args:
            coin (str): 목표가를 구할 종목 코드
            k (float): 종목의 레인지 정보
        Returns:
            target (float): 목표가
        """
        df = await aiopyupbit.get_ohlcv(ticker=coin, interval=self.period, count=2)
        previous_candle = df.iloc[-2]
        return previous_candle['close'] + (previous_candle['high'] - previous_candle['low']) * k

    async def __get_check_list(self, target_price: dict) -> list:
        return [aio.create_task(self.__is_reached(x, target_price[x.code])) for x in self.coin_list]

    async def __loop(self):
        while self.alive:
            self.coin_list = await self.get_best_coin_list()
            k_dict = {x.code: await self.get_best_k(x.code) for x in self.coin_list}
            target_price = {x.code: await self.get_target_price(x.code, k_dict[x.code]) for x in self.coin_list}
            log.info(f'k: {k_dict}\n'
                     f'target_price: {target_price}')

            now = datetime.datetime.now()
            end_time = datetime.datetime.now().replace(hour=static.STRATEGY_DAILY_FINISH_TIME,
                                                       minute=0, second=0, microsecond=0)
            # TODO duration 값에 따른 시간 범위 조정 코드 구현 필요
            if now.hour > static.STRATEGY_DAILY_FINISH_TIME:
                end_time = end_time + datetime.timedelta(days=1)
            log.info(f'Volatility breakout strategy finish at {end_time}')

            while datetime.datetime.now() < end_time:
                check_list = await self.__get_check_list(target_price=target_price)
                check_result = list(filter(None, await aio.gather(*check_list)))
                log.info(f'check_result: {check_result}')
                for code in check_result:
                    self.send_signal(code=code, position='bid',
                                     type='limit', price=target_price)
                time.sleep(1)

            # 모두 매도
            for coin in self.coin_list:
                self.send_signal(code=coin.code, position='ask',
                                 type='market', price=-1)

    async def __is_reached(self, coin: Coin, target_price: float):
        log.info(
            f'code: {coin.code}, target_price: {target_price}, current_price: {coin.get_trade_price()}')
        return coin.code if coin.get_trade_price() >= target_price else None


class VariousIndicatorStrategy(Strategy):
    def __init__(self, queue: Queue, period: int = 14, rsi: int = 35) -> None:
        super().__init__(queue=queue)
        self.period = period
        self.rsi = rsi

    def run(self) -> None:
        """Strategy 모니터링 시작
        """
        log.info('Start various indicator strategy thread')
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        loop.run_until_complete(self.__loop())

    def terminate(self) -> None:
        """Strategy 모니터링 종료
        """
        log.info('Stop various indicator strategy thread')
        self.alive = False
        return super().terminate()

    async def get_best_coin_list(self):
        log.info('Find best target coins, it will spend 60 sec...')
        candidate_list = []
        while True:
            for coin in static.chart.codes:
                df = await aiopyupbit.get_ohlcv(coin, interval='minute5', count=20)
                avg_5 = self.get_average(df, unit=5, column='close')[0]
                avg_10 = self.get_average(df, unit=10, column='close')[0]
                avg_20 = self.get_average(df, unit=20, column='close')[0]

                if (avg_5 > avg_10) and (avg_10 > avg_20):
                    candidate_list.append(coin)
                time.sleep(0.2)

            if candidate_list:
                break

            log.info('Cannot find best target coins, it will re-working again...')

        return [x for x in static.chart.coins.values() if x.code in candidate_list]

    def get_rsi(self, df: DataFrame):
        """rsi 값을 얻는 함수
        Args:
            df (DataFrame): 캔들봉 정보가 담긴 DataFrame
        Returns:
            (DataFrame): rsi 데이터가 있는 DataFrame
        """
        return talib.RSI(np.asarray(df['close']), self.period)

    async def __loop(self):
        time_history = {}
        coin_list = await self.get_best_coin_list()
        log.info(f'Coin list: {[x.code for x in coin_list]}')
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
        log.info(f'Refresh at {end_time}')
        while self.alive:
            # 30분 경과시 전량 매도
            if datetime.datetime.now() >= end_time:
                for coin in coin_list:
                    self.send_signal(code=coin.code, position='ask',
                                     type='market', price=-1)
                # 코인 목록 갱신
                coin_list = await self.get_best_coin_list()
                end_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
                log.info(f'Coin list: {[x.code for x in coin_list]}')
                log.info(f'Refresh at {end_time}')

            for coin in coin_list:
                time.sleep(0.2)
                candle = await aiopyupbit.get_ohlcv(ticker=coin.code, interval='minute1')
                rsi = self.get_rsi(candle)[-1]
                average_volume = self.get_average(candle, 5, 'volume')[1]
                status = {}

                # 보유 검사
                status['own'] = True if coin.code in static.account.coins.keys(
                ) else False

                # 보유중일 경우
                if status['own']:
                    if not coin.code in time_history.keys():
                        time_history[coin.code] = datetime.datetime.now()

                    buy_history = static.account.coins[coin.code]
                    current_price = coin.get_trade_price()
                    # 수익률 도달시 매매
                    profit = (current_price / buy_history['avg_buy_price']) - 1
                    if profit >= 0.01 or profit <= -0.01:
                        self.send_signal(code=coin.code, position='ask',
                                         type='market', price=-1)
                # 보유중이지 않을 경우
                else:
                    if coin.code in time_history.keys():
                        del time_history[coin.code]

                    # 2. RSI 검사
                    status['rsi'] = True if rsi <= self.rsi else False
                    # 3. Volume 검사
                    status['volume'] = True if candle['volume'].iloc[-2] < average_volume else False
                    if status['rsi'] and status['volume']:
                        self.send_signal(code=coin.code, position='bid',
                                         type='limit', price=coin.get_trade_price())

                log.info(f'code: {coin.code}, status: {status}')
