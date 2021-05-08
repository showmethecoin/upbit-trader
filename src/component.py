# !/usr/bin/python
# -*- coding: utf-8 -*-
import json
import uuid
import asyncio
import threading
import multiprocessing

import pyupbit
import websockets

import config
import static
from static import log


class Coin:
    def __init__(self, _code: str) -> None:
        """생성자

        Args:
            _code (str): 코인 마켓 코드
        """
        # Coin code
        self.code = _code
        # Ticker json message
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
        # Orderbook json message
        self.orderbook = {
            'ty': 'orderbook',
            'cd': '',
            'tms': 0,
            'tas': 0,
            'tbs': 0,
            'obu': [],
            'st': 'SNAPSHOT'
        }
        # Sync thread status
        self.sync_status = False

    def _sync_thread(self) -> None:
        while self.sync_status:
            try:
                information = static.chart.information
                if information['cd'] == self.code:
                    self.information = static.chart.information
            except Exception as e:
                print(self.code, e)

    def sync_start(self) -> None:
        """동기화 시작
        """
        log.info(f'{self.code} sync thread start')
        self.sync_status = True
        self.thread = Thread(target=self._sync_thread, daemon=True)
        self.thread.start()

    def sync_stop(self) -> None:
        """동기화 중지
        """
        log.info(f'{self.code} sync thread stop')
        self.sync_status = False

    def get_sync_status(self) -> bool:
        """동기화 동작 상태 반환

        Returns:
            bool: 동기화 동작 유무
        """
        return self.sync_status

    def get_code(self) -> str:
        """코인 마켓 코드 반환

        Returns:
            str: 통화(KRW/BTC)-코드(XXX)
        """
        return self.code

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


class WebsocketManager(multiprocessing.Process):
    def __init__(self, code:str or list, queue:multiprocessing.Queue):
        self.alive = False
        # Upbit websocket json request body
        self.request = json.dumps([
            {"ticket": str(uuid.uuid4())[:6]},
            {"type": "ticker", "codes": code, "isOnlyRealtime": True},
            {"type": "orderbook", "codes": code, "isOnlyRealtime": True},
            {"format": "SIMPLE"}
        ])
        self.__queue = queue
        super().__init__()

    def run(self):
        self.alive = True
        self.__loop = asyncio.get_event_loop()
        self.__loop.run_until_complete(self.__connect_socket())

    def terminate(self):
        self.alive = False
        super().terminate()

    async def __connect_socket(self):
        uri = "wss://api.upbit.com/websocket/v1"
        async with websockets.connect(uri, ping_interval=60) as websocket:
            await websocket.send(self.request)
            while self.alive:
                message = await websocket.recv()
                self.__queue.put(json.loads(message.decode('utf8')))

class RealtimeManager:
    def __init__(self) -> None:
        """생성자
        """
        self.codes = asyncio.run(pyupbit.get_tickers(fiat=config.FIAT))
        self.coins = {code:Coin(code) for code in self.codes}
        self.alive = False
        self.__queue = multiprocessing.Queue()
    
    def get_coin(self, _code: str) -> Coin:
        return self.coins[_code]

    def start(self):
        self.alive = True
        self._websocket = WebsocketManager(code=self.codes, queue=self.__queue)
        self._websocket.start()
        threading.Thread(target=self._sync_thread, daemon=True).start()
    
    def stop(self):
        self._websocket.terminate()
        self.alive = False
    
    def _sync_thread(self):
        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)
        self.__loop.run_until_complete(self.__sync_loop())
    
    async def __sync_loop(self):
        while self.alive:
            message = self.__queue.get()
            if message['ty'] == 'ticker':
                self.coins[message['cd']].ticker = message
            else:
                self.coins[message['cd']].orderbook = message


class Account:
    def __init__(self, _access_key, _secret_key) -> None:
        self._access_key = _access_key
        self._secret_key = _secret_key
        #self._upbit = pyupbit.Upbit(_access_key, _secret_key)
        self.cash = 0.0
        self.total_purchase = 0.0
        self.total_avaluate = 0.0
        self.sync_status = False

    def _sync_thread(self) -> None:
        while self.sync_status:
            try:
                total_purchase = 0
                total_avaluate = 0
                for item in asyncio.run(static.upbit.get_balances()):
                    currency = item["currency"]
                    balance = float(item["balance"])

                    if currency == 'KRW':
                        self.cash = balance
                        #total_purchase += balance
                        #total_avaluate += balance
                    else:
                        purchase = round(
                            balance * float(item["avg_buy_price"]), 0)
                        avaluate = round(balance * static.chart.get_coin("%s-%s" %
                                                                         (config.FIAT, currency)).get_trade_price(), 0)
                        loss = avaluate - purchase
                        total_purchase += purchase
                        total_avaluate += avaluate

                self.total_purchase = total_purchase
                self.total_avaluate = total_avaluate
            except Exception as e:
                print(e)

    def sync_start(self) -> None:
        """동기화 시작
        """
        self.sync_status = True
        self.thread = Thread(target=self._sync_thread, daemon=True)
        self.thread.start()

    def sync_stop(self) -> None:
        """동기화 중지
        """
        self.sync_status = False

    def get_sync_status(self) -> bool:
        """동기화 동작 상태 반환
        """
        return self.sync_status

    def get_cash(self) -> float:
        """총 보유 현금
        """
        return self.cash

    def get_buy_price(self) -> float:
        """총 구매 비용
        """
        return self.total_purchase

    def get_trade_price(self) -> float:
        """총 현재 가격
        """
        return self.total_avaluate

    def get_total_loss(self) -> float:
        """총 손익 가격
        """
        return (self.total_avaluate - self.total_purchase)


if __name__ == '__main__':

    # NOTE Windows 운영체제 환경에서 Python 3.7+부터 발생하는 EventLoop RuntimeError 관련 처리
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
	    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Upbit coin chart
    # static.chart = Chart()
    # static.chart.sync_start()
    test = RealtimeManager()
    test.start()
    

    # User upbit connection
    static.upbit = pyupbit.Upbit(
        config.UPBIT["ACCESS_KEY"], config.UPBIT["SECRET_KEY"])

    # # Upbit account
    # static.account = Account(config.UPBIT["ACCESS_KEY"], config.UPBIT["SECRET_KEY"])
    # static.account.sync_start()

    while(True):
        import time
        time.sleep(1)
