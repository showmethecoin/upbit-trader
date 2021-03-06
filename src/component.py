# !/usr/bin/python
# -*- coding: utf-8 -*-
import json
import uuid
import time
import asyncio as aio
from threading import Thread
from multiprocessing import Queue, Process

import websockets
import aiopyupbit

import static
from static import log


class Coin:
    def __init__(self, code: dict) -> None:
        """생성자

        Args:
            _code (str): 코인 마켓 코드
        """
        # Public
        self.code = code['market']
        self.korean_name = code['korean_name']
        self.english_name = code['english_name']
        self.ticker = {
            'ty': 'ticker',
            'cd': '',
            'op': 0,
            'hp': 0,
            'lp': 0,
            'tp': 0,
            'pcp': 0,
            'atp': 0,
            'c': 'RISE',
            'cp': 0,
            'scp': 0,
            'cr': 0,
            'scr': 0,
            'ab': 'BID',
            'tv': 0,
            'atv': 0,
            'tdt': '0',
            'ttm': '0',
            'ttms': 0,
            'aav': 0,
            'abv': 0,
            'h52wp': 0,
            'h52wdt': 'NONE',
            'l52wp': 0,
            'l52wdt': 'NONE',
            'ts': None,
            'ms': 'UNKNOWN',
            'msfi': None,
            'its': False,
            'dd': None,
            'mw': 'NONE',
            'tms': 0,
            'atp24h': 0,
            'atv24h': 0,
            'st': 'SNAPSHOT'
        }
        self.orderbook = {
            'ty': 'orderbook',
            'cd': '',
            'tms': 0,
            'tas': 0,
            'tbs': 0,
            'obu': [],
            'st': 'SNAPSHOT'
        }

    def get_code(self, fiat=True) -> str:
        """코인 마켓 코드 반환

        Args:
            fiat (bool, optional): 통화 포함 여부. Defaults to True.

        Returns:
            str: 통화(KRW/BTC)-코드(XXX) or 코드(XXX)
        """
        if fiat:
            return self.code
        else:
            return self.code.split('-')[-1]

    def get_opening_price(self) -> float:
        """금일 코인 시작 가격(시가) 반환

        Returns:
            float: 금일 시작 가격
        """
        return self.ticker['op']

    def get_high_price(self) -> float:
        """금일 코인 최고 가격(고가) 반환

        Returns:
            float: 금일 최고 가격
        """
        return self.ticker['hp']

    def get_low_price(self) -> float:
        """금일 코인 최저 가격(저가) 반환

        Returns:
            float: 금일 최저 가격
        """
        return self.ticker['lp']

    def get_trade_price(self) -> float:
        """금일 코인 현재 가격(현재가) 반환

        Returns:
            float: 금일 현재 가격
        """
        return self.ticker['tp']

    def get_prev_closing_price(self) -> float:
        """전일 코인 마감 가격(종가) 반환

        Returns:
            float: 전일 마감 가격
        """
        return self.ticker['pcp']

    def get_acc_trade_price(self) -> float:
        """금일(UTC 0시 기준) 누적 거래 대금 반환

        Returns:
            float: 금일 누적 거래 대금
        """
        return self.ticker['atp']

    def get_change(self) -> str:
        """전일 대비 가격 상태 반환 반환

        Returns:
            str: RISE(상승) or EVEN(보합) or FALL(하락)
        """
        return self.ticker['c']

    def get_change_price(self) -> float:
        """전일 대비 변동 가격(unsigned) 반환

        Returns:
            float: 변동 가격
        """
        return self.ticker['cp']

    def get_signed_change_price(self) -> float:
        """전일 대비 변동 가격(signed) 반환

        Returns:
            float: 변동 가격
        """
        return self.ticker['scp']

    def get_change_rate(self) -> float:
        """전일 대비 등락율(unsigned) 반환

        Returns:
            float: 등락율
        """
        return self.ticker['cr']

    def get_signed_change_rate(self) -> float:
        """전일 대비 등락율(signed) 반환

        Returns:
            float: 등락율
        """
        return self.ticker['scr']

    def get_ask_bid(self) -> str:
        """매수/매도 구분 반환

        Returns:
            str: ASK(매도) or BID(매수)
        """
        return self.ticker['ab']

    def get_trade_volume(self) -> float:
        """가장 최근 거래량 반환

        Returns:
            float: 거래량
        """
        return self.ticker['tv']

    def get_acc_trade_volume(self) -> float:
        """누적 거래량(UTC 0시 기준) 반환

        Returns:
            float: 누적 거래량
        """
        return self.ticker['atv']

    def get_trade_date(self) -> str:
        """최근 거래 일자(UTC) 반환

        Returns:
            str: yyyyMMdd(거래 일자)
        """
        return self.ticker['tdt']

    def get_trade_time(self) -> str:
        """최근 거래 시각 반환

        Returns:
            str: HHmmss(거래 시각)
        """
        return self.ticker['ttm']

    def get_trade_timestamp(self) -> int:
        """체결 타임스탬프(millisec) 반환

        Returns:
            int: 타임스탬프
        """
        return self.ticker['ttms']

    def get_acc_ask_volume(self) -> float:
        """누적 매도량 반환

        Returns:
            float: 매도량
        """
        return self.ticker['aav']

    def get_acc_bid_volume(self) -> float:
        """누적 매수량 반환

        Returns:
            float: 매수량
        """
        return self.ticker['abv']

    def get_highest_52_week_price(self) -> float:
        """52주 최고 가격(최고가) 반환

        Returns:
            float: 최고 가격
        """
        return self.ticker['h52wp']

    def get_highest_52_week_date(self) -> str:
        """52주 최고 가격(최고가) 달성일 반환

        Returns:
            str: yyyy-MM-dd(달성일)
        """
        return self.ticker['h52wdt']

    def get_lowest_52_week_price(self) -> float:
        """52주 최저 가격(최저가) 반환

        Returns:
            float: 최저 가격
        """
        return self.ticker['l52wp']

    def get_lowest_52_week_date(self) -> str:
        """52주 최저 가격(최저가) 달성일 반환

        Returns:
            str: yyyy-MM-dd(달성일)
        """
        return self.ticker['l52wdt']

    def get_trade_status(self) -> str:
        # 거래 상태 *deprecated
        return self.ticker['ts']

    def get_market_state_for_ios(self) -> str:
        # 거래 상태 *deprecated
        return self.ticker['msfi']

    def get_market_state(self) -> str:
        """거래 상태

        Returns:
            str: PREVIEW(입금지원) or ACTIVE(거래지원가능) or DELISTED(거래지원종료)
        """
        return self.ticker['ms']

    def get_is_trading_suspended(self) -> bool:
        """거래 정지 여부 반환

        Returns:
            bool: 정지 여부
        """
        return self.ticker['its']

    def get_delisting_date(self) -> str:
        """상장 폐지일 반환

        Returns:
            str: yyyy-MM-dd(폐지일)
        """
        return self.ticker['dd']

    def get_market_warning(self) -> str:
        """유의 종목 여부 반환

        Returns:
            str: NONE(해당없음) or CAUTION(투자유의)
        """
        return self.ticker['mw']

    def get_timestamp(self) -> int:
        """타임스탬프(millisec) 반환

        Returns:
            int: 타임스탬프
        """
        return self.ticker['tms']

    def get_acc_trade_price_24h(self) -> float:
        """24시간 누적 거래대금 반환

        Returns:
            float: 거래 대금
        """
        return self.ticker['atp24h']

    def get_acc_trade_volume_24h(self) -> float:
        """24시간 누적 거래량 반환

        Returns:
            float: 거래량
        """
        return self.ticker['atv24h']

    def get_stream_type(self) -> str:
        """스트림 타입 반환

        Returns:
            str: SNAPSHOT(스냅샷) or REALTIME(실시간)
        """
        return self.ticker['st']

    def get_total_ask_size(self) -> float:
        """호가 매도 총 잔량 반환

        Returns:
            float: 총 잔량
        """
        return self.orderbook['tas']

    def get_total_bid_size(self) -> float:
        """호가 매수 총 잔량 반환

        Returns:
            float: 총 잔량
        """
        return self.orderbook['tbs']

    def get_orderbook_units(self, _index: int = 0) -> dict or list:
        """호가 반환

        ap -> float: 매도 호가
        bp -> float: 매수 호가
        as -> float: 매도 잔량
        bs -> float: 매수 잔량
        
        Args:
            _index (int, optional): 호가 목록 위치. Defaults to 0.

        Returns:
            dict or list: dict if _index != 0 else list
        """
        if _index == 0:
            return self.orderbook['obu']
        return self.orderbook['obu'][_index]


class WebsocketManager(Process):
    def __init__(self, uri: str, request: dict, ping_interval: int, queue: Queue) -> None:
        """WebsocketManager 생성자

        Args:
            uri (str): Websocket 연결 주소
            request (dict): 요청 메세지 Body
            ping_interval (int): Ping-Pong 주기
            queue (Queue): 수신 메세지 대기열
        """
        # Public
        self.uri = uri
        self.request = request
        self.ping_interval = ping_interval
        self.alive = False
        # Private
        self.__queue = queue

        super().__init__()

    def run(self) -> None:
        """Websocket 연결 시작
        사용 예시: wm.start()
        """
        log.info('Start websocket connection')
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        loop.run_until_complete(self.__connect_socket())

    def terminate(self) -> None:
        """Websocket 연결 종료
        사용 예시: wm.terminate()
        """
        log.info('Stop websocket connection')
        self.alive = False
        super().terminate()

    async def __connect_socket(self) -> None:
        """Websocket async 루프 메인
        """
        async with websockets.connect(self.uri, ping_interval=self.ping_interval) as websocket:
            while self.alive:
                try:
                    await websocket.send(self.request)
                    while self.alive:
                        message = await websocket.recv()
                        self.__queue.put(json.loads(message.decode('utf8')))
                except websockets.exceptions.ConnectionClosedError:
                    log.warning(
                        f'Websocket connection closed. It will try to connect again')


class RealtimeManager:
    def __init__(self, 
                 codes: list,
                 ping_interval:int=60) -> None:
        """RealtimeManager 생성자
        """
        # Public
        self.codes = [x['market'] for x in codes]
        self.sort_status = {'method': None,
                            'ordered': None}
        self.coins = {code['market']: Coin(code) for code in codes}
        self.uri = "wss://api.upbit.com/websocket/v1"
        self.request = json.dumps([
            {"ticket": str(uuid.uuid4())[:6]},
            {"type": "ticker", "codes": self.codes, "isOnlyRealtime": True},
            {"type": "orderbook", "codes": self.codes, "isOnlyRealtime": True},
            {"format": "SIMPLE"}
        ])
        self.ping_interval = ping_interval
        self.alive = False
        # Private
        self.__origin_coins = self.coins
        self.__queue = Queue()

    def get_coin(self, code: str) -> Coin:
        """코인 반환

        Args:
            code (str): 코인 코드

        Returns:
            Coin: 코드에 해당하는 Coin 인스턴스
        """
        return self.coins[code]

    def sort(self, target: str):
        if target == 'code':
            if self.sort_status['method'] != 'code':
                self.coins = {x: y for x, y in sorted(self.coins.items(),
                                                   key=lambda x: x[1].korean_name)}
                self.sort_status['method'] = 'code'
                self.sort_status['ordered'] = 'ascending'
            elif self.sort_status['ordered'] == 'ascending':
                self.coins = self.coins = {x: y for x, y in sorted(self.coins.items(),
                                                   key=lambda x: x[1].korean_name, reverse=True)}
                self.sort_status['ordered'] = 'descending'
            else:
                self.coins = self.__origin_coins
                self.sort_status['method'] = None
                self.sort_status['ordered'] = None
        elif target == 'value':
            if self.sort_status['method'] != 'value':
                self.coins = {x: y for x, y in sorted(self.coins.items(),
                                                   key=lambda x: x[1].get_trade_price(), reverse=True)}
                self.sort_status['method'] = 'value'
                self.sort_status['ordered'] = 'ascending'
            elif self.sort_status['ordered'] == 'ascending':
                self.coins = {x: y for x, y in sorted(self.coins.items(),
                                                   key=lambda x: x[1].get_trade_price())}
                self.sort_status['ordered'] = 'descending'
            else:
                self.coins = self.__origin_coins
                self.sort_status['method'] = None
                self.sort_status['ordered'] = None
        elif target == 'change':
            if self.sort_status['method'] != 'change':
                self.coins = {x: y for x, y in sorted(self.coins.items(),
                                                   key=lambda x: x[1].get_signed_change_rate(), reverse=True)}
                self.sort_status['method'] = 'change'
                self.sort_status['ordered'] = 'ascending'
            elif self.sort_status['ordered'] == 'ascending':
                self.coins = {x: y for x, y in sorted(self.coins.items(),
                                                   key=lambda x: x[1].get_signed_change_rate())}
                self.sort_status['ordered'] = 'descending'
            else:
                self.coins = self.__origin_coins
                self.sort_status['method'] = None
                self.sort_status['ordered'] = None

    def start(self) -> None:
        """RealtimeManager 동기화 시작
        """
        self.alive = True
        self._websocket = WebsocketManager(
            uri=self.uri,
            request=self.request,
            ping_interval=self.ping_interval,
            queue=self.__queue)
        self._websocket.start()
        Thread(target=self._sync_thread, daemon=True).start()

    def stop(self) -> None:
        """RealtimeManager 동기화 종료
        """
        self._websocket.terminate()
        self.alive = False

    def _sync_thread(self) -> None:
        """동기화 Thread 메인
        """
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        loop.run_until_complete(self.__sync_loop())

    async def __sync_loop(self) -> None:
        """동기화 async 루프 메인
        """
        while self.alive:
            message = self.__queue.get()
            if message['ty'] == 'ticker':
                self.coins[message['cd']].ticker = message
            else:
                self.coins[message['cd']].orderbook = message


class Account(Thread):
    def __init__(self, access_key:str, secret_key:str) -> None:
        
        super().__init__()
        
        # Public
        self.alive = False
        self.daemon = True
        self.access_key = access_key
        self.secret_key = secret_key
        self.upbit = aiopyupbit.Upbit(self.access_key, self.secret_key)
        
        self.coins = {}
        self.cash = 0.0
        self.locked_cash = 0.0
        self.total_purchase = 0
        self.total_evaluate = 0
        self.total_loss = 0
        self.total_yield = 0.0

    def run(self) -> None:
        log.info('Start account thread')
        self.alive = True
        loop = aio.new_event_loop()
        aio.set_event_loop(loop)
        loop.run_until_complete(self.__loop())
    
    def terminate(self) -> None:
        log.info('Stop account thread')
        self.alive = False
        return super().terminate()
      
    async def __loop(self) -> None:
        while self.alive:
            try:
                time.sleep(0.25)
                coins = {}
                cash = 0
                locked_cash = 0
                total_purchase = 0
                total_evaluate = 0
                total_loss = 0
                total_yield = 0

                for item in await self.upbit.get_balances():
                    currency = item['currency']
                    avg_buy_price = float(item['avg_buy_price'])
                    balance = float(item['balance'])
                    locked = float(item['locked'])
                    if currency == 'KRW':
                        cash = round(balance, 0)
                        locked_cash = round(locked, 0)
                    elif currency == 'XYM':
                        continue
                    else:
                        if(currency == 'VTHO'):
                            continue
                        coin = static.chart.get_coin("%s-%s" %(static.FIAT, currency))
                        purchase = (balance + locked) * avg_buy_price
                        evaluate = (balance + locked) * coin.get_trade_price()
                        loss = evaluate - purchase
                        data = {}
                        data['currency'] = currency
                        data['balance'] = balance
                        data['locked'] = locked
                        data['avg_buy_price'] = avg_buy_price
                        data['purchase'] = purchase
                        data['evaluate'] = evaluate
                        data['loss'] = loss
                        data['yield'] = loss / purchase * 100
                        coins[currency] = data
                        total_purchase += purchase
                        total_evaluate += evaluate
                        
                total_loss = total_evaluate - total_purchase
                if total_purchase != 0:
                    total_yield = total_loss / total_purchase * 100
                
                self.coins = coins
                self.cash = cash
                self.locked_cash = locked_cash
                self.total_purchase = total_purchase
                self.total_evaluate = total_evaluate
                self.total_loss = total_loss
                self.total_yield = total_yield

            except Exception as e:
                import traceback
                print(traceback.format_exc())
                print(e)

    def get_cash(self) -> float:
        """보유 현금
        """
        return self.cash

    def get_locked_cash(self) -> float:
        """매수 걸어 놓은 현금
        """
        return self.locked_cash

    def get_total_cash(self) -> float:
        """총 보유 현금
        """
        return self.cash + self.locked_cash

    def get_buy_price(self) -> float:
        """총 매수 비용
        """
        return self.total_purchase

    def get_evaluate_price(self) -> float:
        """총 평가 가격
        """
        return self.total_evaluate

    def get_total_holding_price(self) ->float:
        return self.cash + self.locked_cash + self.total_evaluate

    def get_total_loss(self) -> float:
        """총 손익 가격
        """
        return self.total_loss

    def get_total_yield(self) -> float:
        """총 수익률
        """
        return self.total_yield


if __name__ == '__main__':
    import time
    from config import Config
    from utils import set_windows_selector_event_loop_global
    
    set_windows_selector_event_loop_global()

    static.config = Config()
    static.config.load()
    
    loop = aio.new_event_loop()
    aio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=static.FIAT, contain_name=True))
    static.chart = RealtimeManager(codes=codes)
    static.chart.start()

    # Upbit account
    static.account = Account(access_key=static.config.upbit_access_key,
                             secret_key=static.config.upbit_secret_key)
    static.account.start()

    while(True):
        time.sleep(1)
