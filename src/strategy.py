# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime
import asyncio
import multiprocessing
import threading

import numpy as np
import aiopyupbit
from pandas.core.frame import DataFrame
import talib

import component
import db
import static
from static import log


class SignalManager(multiprocessing.Process):
    def __init__(self, queue: multiprocessing.Queue) -> None:
        # Public
        self.alive = False
        # Private
        self.queue = queue

        super().__init__()

    def run(self) -> None:
        """SignalManager 시작
        """
        log.info('Start signal manager process')
        self.alive = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__loop())

    def terminate(self) -> None:
        """SignalManager 종료
        """
        log.info('Stop signal manager process')
        self.alive = False
        return super().terminate()

    async def __loop(self) -> None:
        price = 10000
        while self.alive:
            try:
                message = self.queue.get()
                log.info(f'Signal information:\n'
                         f'code: {message["code"]}\n'
                         f'type: {message["type"]}\n'
                         f'position: {message["position"]}\n'
                         f'price: {message["price"]}')

                # if message['position'] == 'bid':
                #     code = message['code'].split('-')[1]
                #     order_list = static.upbit.get_order(message['code'])
                #     if code in static.account.coins.keys():
                #         log.warning(f'{code} is already bought')
                #     elif order_list:
                #         log.warning(f'order_list: {order_list}')
                #         # TODO 취소하고 살건지, 그냥 살건지, 여러개있으면 어떡할지 ...
                #     else:
                #         if message['type'] == 'market':
                #             static.upbit.buy_market_order(
                #                 ticker=message['code'], price=price)
                #         else:
                #             static.upbit.buy_limit_order(
                #                 ticker=message['code'], price=message['price'], volume=price/message['price'])
                # else:
                #     if not code in static.account.coins.keys():
                #         log.warning(f'{code} is not bought')
                #     elif order_list:
                #         log.warning(f'order_list: {order_list}')
                #         # TODO 취소하고 살건지, 그냥 살건지, 여러개있으면 어떡할지 ...
                #     else:
                #         if message['type'] == 'market':
                #             static.upbit.sell_market_order(
                #                 ticker=message['code'], price=static.account.coins[message.code]['balance'])
                #         else:
                #             static.upbit.sell_limit_order(
                #                 ticker=message['code'], price=message['price'], volume=static.account.coins[message.code]['balance'])
            except Exception as e:
                log.error(e)


class Strategy(threading.Thread):
    def __init__(self, queue: multiprocessing.Queue) -> None:
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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
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
    def __init__(self, coin_list: list, queue: multiprocessing.Queue, period: str = 'day') -> None:
        super().__init__(queue=queue)
        # 투자 대상 Coin 인스턴스 목록
        self.coin_list = coin_list
        self.period = period

    def run(self) -> None:
        """Strategy 모니터링 시작
        """
        log.info('Start volatility breakout strategy thread')
        self.alive = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__loop())

    def terminate(self) -> None:
        """Strategy 모니터링 종료
        """
        log.info('Stop volatility breakout strategy thread')
        self.alive = False
        return super().terminate()

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
        log.info(code)
        df = df.iloc[:-1]
        df['noise'] = 1 - abs(df['open']-df['close']) / (df['high']-df['low'])
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
        return [asyncio.create_task(self.__is_reached(x, target_price[x.code])) for x in self.coin_list]

    async def __loop(self):
        while self.alive:
            # k_dict = {x.code: await self.get_best_k(x.code) for x in self.coin_list}
            k_dict = {x.code: 0.000000000001 for x in self.coin_list}
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
                check_result = list(filter(None, await asyncio.gather(*check_list)))
                log.info(f'check_result: {check_result}')
                for code in check_result:
                    self.send_signal(code=code, position='bid',
                                     type='limit', price=target_price)
                time.sleep(1)

            # 모두 매도
            for coin in self.coin_list:
                self.send_signal(code=coin.code, position='ask',
                                 type='market', price=-1)

    async def __is_reached(self, coin: component.Coin, target_price: float):
        log.info(f'code: {coin.code}, target_price: {target_price}, current_price: {coin.get_trade_price()}')
        return coin.code if coin.get_trade_price() >= target_price else None


# class VariousIndicatorStrategy(Strategy):
#     def __init__(self, coin_list: list, queue: multiprocessing.Queue, period: int = 14) -> None:
#         super().__init__(queue=queue)
#         # 투자 대상 Coin 인스턴스 목록
#         self.coin_list = coin_list
#         self.period = period

#     def run(self) -> None:
#         """Strategy 모니터링 시작
#         """
#         log.info('Start volatility breakout strategy process')
#         self.alive = True
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         loop.run_until_complete(self.__loop())

#     def terminate(self) -> None:
#         """Strategy 모니터링 종료
#         """
#         log.info('Stop volatility breakout strategy process')
#         self.alive = False
#         return super().terminate()
    
#     def get_rsi(self, df: DataFrame):
#         """rsi 값을 얻는 함수
#         Args:
#             df (DataFrame): 캔들봉 정보가 담긴 DataFrame
#         Returns:
#             (DataFrame): rsi 데이터가 있는 DataFrame
#         """
#         return talib.RSI(np.asarray(df['close']), self.period)


# async def various_indicator_strategy(coin_list, period):

#     while True:
#         for coin in coin_list:
#             time.sleep(0.1)

#             is_changed = False

#             #현재가 저장
#             cur_price = coin.get_trade_price()

#             #200개의 캔들봉을 얻은 후 rsi 데이터 저장
#             df = await aiopyupbit.get_ohlcv(coin.code, count=200, interval='minute1')
#             rsi = get_rsi_data(df, period)[-1]

#             # print(datetime.datetime.now(),'\t',int(rsi),'\t',coin.code)

#             #매도 검사
#             if buy_data[coin.code]['buy_price'] > 0:
#                 profit_ratio_rate = (
#                     cur_price/buy_data[coin.code]['buy_price'])
#                 profit_ratio = (
#                     (cur_price/buy_data[coin.code]['buy_price'])-1)*100
#                 #현재 시간과 매수 시간의 차이 (10분이 넘었으면 그냥 매도)
#                 time_diff = datetime.datetime.now(
#                 ) - buy_data[coin.code]['buy_time']
#                 if profit_ratio >= 1 or profit_ratio <= -1 or time_diff >= datetime.timedelta(minutes=10):
#                     # print('#################매도 진행#################')
#                     print('거래에 걸린 시간 : ', time_diff)
#                     is_changed = True
#                     ct += 1
#                     cumul_profit *= profit_ratio_rate
#                     if time_diff >= datetime.timedelta(minutes=10):
#                         time_sell += 1
#                     else:
#                         if profit_ratio >= 1:
#                             plus += 1
#                         else:
#                             minus += 1
#                     print('=======================')
#                     print('완료 횟수 : ', ct)
#                     print('익절 횟수 : ', plus)
#                     print('손절 횟수 : ', minus)
#                     print('시간 매도 : ', time_sell)
#                     print('승률 : ', plus/ct*100, '%')
#                     print('누적수익률 : ', (cumul_profit-1)*100)
#                     print('=======================')
#                     print('')
#                     #매도 signal
#                     send_signal(coin.code, 'ask', cur_price)

#                     #투자 결과를 DB에 삽입
#                     res_dict = {}
#                     now = datetime.datetime.now()
#                     now = datetime.datetime(
#                         now.year, now.month, now.day, now.hour, now.minute, now.second)
#                     res_dict['_id'] = time.mktime(datetime.datetime.strptime(str(now),
#                                                                              static.BASE_TIME_FORMAT).timetuple())
#                     res_dict['time'] = str(now)
#                     res_dict['buy price'] = buy_data[coin.code]['buy_price']
#                     res_dict['sell price'] = cur_price
#                     res_dict['buy RSI'] = buy_data[coin.code]['buy_rsi']
#                     res_dict['profit ratio'] = profit_ratio
#                     res_dict['time diff'] = buy_data[coin.code]['buy_time'] - \
#                         datetime.datetime.now()

#                     # await static.db.insert_item_one(data=res_dict,
#                     #                                 db_name='strategy_various_indicator',
#                     #                                 collection_name=coin.code)
#                     print('------------------------------------------')
#                     # print(coin.code,' DB 삽입 완료')
#                     for x in res_dict.items():
#                         print(x[0], x[1])
#                     print(buy_data[coin.code])
#                     print('------------------------------------------')

#                     #구매기록 초기화
#                     buy_data[coin.code]['buy_price'] = -1
#                     buy_data[coin.code]['buy_rsi'] = -1
#                     buy_data[coin.code]['buy_time'] = -1

#             #매수 signal
#             else:
#                 avg_volume = get_avg(df, 5, 'volume')[0]
#                 # avg_5 = get_avg(df,5)[0]
#                 # avg_10 = get_avg(df,10)[0]
#                 # avg_20 = get_avg(df,10)[0]

#                 # and avg_5 > avg_10 > avg_20:
#                 if rsi <= 35 and df.loc[0]['volume'] < avg_volume:
#                     # print(coin.code,': 매수 신호, rsi : ',rsi,' 현재 거래량 : ',df.loc[0]['volume'],' 5분 평균 거래량 : ',avg_volume)

#                     if buy_data[coin.code]['buy_price'] != -1:
#                         continue
#                     is_changed = True
#                     #매수 진행
#                     # print('#################매수 진행#################')
#                     send_signal(coin.code, 'bid', cur_price)
#                     buy_data[coin.code]['buy_time'] = datetime.datetime.now()
#                     buy_data[coin.code]['buy_price'] = cur_price
#                     buy_data[coin.code]['buy_rsi'] = rsi
#                     print('------------------------------------------')
#                     print(coin.code, ' 매수 후 buy_data')
#                     print(buy_data[coin.code])
#                     # for x in buy_data[coin.code]:
#                     #     print(x[0],x[1])
#                     print('------------------------------------------')
