from types import DynamicClassAttribute, TracebackType
from aiopyupbit.request_api import _send_delete_request
import numpy as np
import pandas as pd
import time
import aiopyupbit
import datetime
import asyncio
import talib
import component
import db
import config
import static
from static import log

from db import DBHandler

signal = []

def send_signal(coin,type,req_price):
    """매수, 매도 signal을 보내는 함수
    Args:
        coin (str): 종목 이름
        type (str): ask(매도), bid(매수)
        req_price (float): 요청 가격
    """
    signal.append({'ticker':coin,'type':type,'req_price':req_price})
    print(signal[-1])
def get_avg(df,unit=5,column='close'):
    """unit 동안의 평균값을 리턴하는 함수
    Args:
        df (DataFrame): 캔들봉 정보가 담긴 DataFrame
        unit (int): 평균을 구할 기간
        column (str): 평균을 구할 column
    Returns:
        (float): 해당 column의 평균값을 리턴
    """
    return df[column].rolling(unit).mean()

def get_rsi_data(df, period=14):
    """rsi 값을 얻는 함수
    Args:
        df (DataFrame): 캔들봉 정보가 담긴 DataFrame
        period (int): rsi값을 구할 기간
    Returns:
        (DataFrame): rsi 데이터가 있는 DataFrame
    """
    return talib.RSI(np.asarray(df['close']), period)

async def get_best_k(coin):
    """백테스팅을 통해 최적의 k를 찾는 함수
    Args:
        coin (str): k를 얻을 종목 코드
    Returns:
        백테스팅을 통해 찾은 최적의 k
    """
    time.sleep(0.1)
    df = await aiopyupbit.get_ohlcv(coin,interval='minute60',count=21)
    df = df.iloc[:-1]
    df['noise']= 1 - abs(df['open']-df['close']) / (df['high']-df['low'])
    return df['noise'].mean()

async def get_target_price(coin,k_data):
    """목표가격을 얻는 함수
    Args:
        coin (str): 목표가를 구할 종목 코드
        k_data (float): 종목의 레인지 정보
    Returns:
        target (float): 목표가
    """ 
    time.sleep(0.1)
    df = await aiopyupbit.get_ohlcv(coin,interval='minute240',count=2)
    # df = await aiopyupbit.get_ohlcv(coin,interval='minute60',count=2)
    prio = df.iloc[-2]
    curr_open = prio['close']
    prio_high = prio['high']
    prio_low = prio['low']
    target = curr_open + (prio_high - prio_low) * k_data
    return target

async def volatility_breakout_strategy(k_input=None,coin_list=None):
    """변동성 돌파 전략
    Args:
        k_input (dict): {'KRW-BTC' : 0.6, 'KRW-XRP' : 0.1, 'KRW-BTT' : 0.9, ..}
        coin_list (list): ['KRW-BTC', 'KRW-XRP', 'KRW-BTT', ..]
    """
    # if static.upbit == None:
    #     return
    static.upbit = aiopyupbit.Upbit(static.config.upbit_access_key, static.config.upbit_secret_key)

    #DB 설정
    if static.db == None:
        static.db = db.DBHandler(ip=static.config.mongo_ip,
                              port=static.config.mongo_port,
                              id=static.config.mongo_id,
                              password=static.config.mongo_password)

    #투자할 종목들의 coin 객체를 저장
    coin_list = [x for x in static.chart.coins.values() if x.code in coin_list]

    #종목별 k 설정 (입력값 제외한 나머지는 백테스팅을 통해 설정)
    k_dict = {x.code : await get_best_k(x.code) for x in coin_list if x not in k_input.keys()}
    k_dict.update(k_input)

    #초기 목표가 설정
    target_price = {x.code : await get_target_price(x.code,k_dict[x.code]) for x in coin_list}

    #구매 기록 df 초기화 (구매 정보를 저장)
    buy_price = {x.code : -1 for x in coin_list}

    #투자 횟수 초기화 (몇번 투자 시도할 것인지)
    count = 0

    #투자 기간 정하기 (시간)
    term = 4
    # term = 1
    term_hour = True
    term_day = False
    time_log = {x:False for x in range(0,24)}

    #지정 횟수만큼 투자 진행
    while count < 5:
        #지정 종목에 대해 투자
        for coin in coin_list:
            now = datetime.datetime.now()
            print('현재시간 : ',now)

            #term 간격으로 목표가 정하고 수익률 계산
            if now.hour in [1,5,9,13,17,21] and time_log[now.hour] == False:
            # if time_log[now.hour] == False: #돌아가고 있는 시간대가 아닌 경우에만 실행
            # if True: #테스트 코드
                mid = datetime.datetime(now.year, now.month, now.day, now.hour) #정상 코드
                # mid = datetime.datetime(now.year, now.month, now.day, now.hour,33) #테스트 코드 (검사 종료할 minute)

                #매도 및 목표가, K 업데이트
                if mid < now < mid + datetime.timedelta(seconds=1):
                    #매수한 종목을 모두 매도
                    for coin_data in coin_list:
                        cur_price = coin_data.get_trade_price()
                        #매수한 경우 ask signal
                        if buy_price[coin_data.code] > 0:
                            send_signal(coin_data.code,'ask',cur_price)

                    #종목별 k 갱신 (입력값 제외한 나머지는 백테스팅을 통해 설정)
                    k_dict = {x.code : await get_best_k(x.code) for x in coin_list if x not in k_input.keys()}
                    k_dict.update(k_input)

                    #각 코인의 목표가 갱신
                    target_price = {x.code : await get_target_price(x.code,k_dict[x.code]) for x in coin_list}

                    #각 코인의구매기록 초기화
                    buy_price = {x.code : -1 for x in coin_list}

                    #투자 횟수 + 1
                    count += 1
                    
                    #시간 기록 변경
                    time_log[now.hour] = True
                    prio_hour = now.hour - term
                    time_log[prio_hour] = False

                    time.sleep(0.5)

            #매수한 이력이 있으면 검사하지 않음
            if buy_price[coin.code] > 0:
                continue

            #현재가격과 목표가를 비교
            cur_price = coin.get_trade_price()            
            if cur_price < target_price[coin.code]:
                continue
            else: #현재 k에서 매수 저장
                send_signal(coin.code,'bid',cur_price)
                buy_price[coin.code] = cur_price
    exit()

async def various_indicator_strategy(coin_list,period):
    """rsi, 거래량 기반 투자 전략
    Args:
        coin_list (list): ['KRW-BTC', 'KRW-XRP', 'KRW-BTT', ..]
        period (int): rsi 기간 설정 값
    """
    # if static.upbit == None:
        #     return
    static.upbit = aiopyupbit.Upbit(static.config.upbit_access_key, static.config.upbit_secret_key)

    #DB 설정
    if static.db == None:
        static.db = db.DBHandler(ip=static.config.mongo_ip,
                              port=static.config.mongo_port,
                              id=static.config.mongo_id,
                              password=static.config.mongo_password)
    
    #투자할 종목들의 coin 객체를 저장
    coin_list = await aiopyupbit.get_tickers(fiat='KRW')
    coin_list = [x for x in static.chart.coins.values() if x.code in coin_list]

    #구매 기록 df 초기화 (구매 정보를 저장)
    buy_data = {x.code : {'buy_time' : -1,'buy_price' : -1, 'buy_rsi' : -1} for x in coin_list}
    # print('------------------------------------------')
    # print('초기 buy_data')
    # for x in buy_data.items():
    #     print(x[0],x[1])
    ct = 0
    plus = 0
    minus = 0
    time_sell = 0

    cumul_profit = 1
    while True:
        for coin in coin_list:
            time.sleep(0.1)
            
            is_changed = False

            #현재가 저장
            cur_price = coin.get_trade_price()
            
            #200개의 캔들봉을 얻은 후 rsi 데이터 저장
            df = await aiopyupbit.get_ohlcv(coin.code,count = 200,interval = 'minute1')
            rsi = get_rsi_data(df, period)[-1]

            # print(datetime.datetime.now(),'\t',int(rsi),'\t',coin.code)

            #매도 검사
            if buy_data[coin.code]['buy_price'] > 0:
                profit_ratio_rate = (cur_price/buy_data[coin.code]['buy_price'])
                profit_ratio = ((cur_price/buy_data[coin.code]['buy_price'])-1)*100
                #현재 시간과 매수 시간의 차이 (10분이 넘었으면 그냥 매도)
                time_diff = datetime.datetime.now() - buy_data[coin.code]['buy_time']
                if profit_ratio >= 1 or profit_ratio <= -1 or time_diff >= datetime.timedelta(minutes=10):
                    # print('#################매도 진행#################')
                    print('거래에 걸린 시간 : ',time_diff)
                    is_changed = True
                    ct += 1
                    cumul_profit *= profit_ratio_rate
                    if time_diff >= datetime.timedelta(minutes=10):
                        time_sell += 1
                    else:
                        if profit_ratio >= 1:
                            plus += 1
                        else:
                            minus += 1
                    print('=======================')
                    print('완료 횟수 : ',ct)
                    print('익절 횟수 : ',plus)
                    print('손절 횟수 : ',minus)
                    print('시간 매도 : ',time_sell)
                    print('승률 : ',plus/ct*100,'%')
                    print('누적수익률 : ',(cumul_profit-1)*100)
                    print('=======================')
                    print('')
                    #매도 signal
                    send_signal(coin.code,'ask',cur_price)

                    #투자 결과를 DB에 삽입
                    res_dict = {}
                    now = datetime.datetime.now()
                    now = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
                    res_dict['_id'] = time.mktime(datetime.datetime.strptime(str(now),
                                                static.BASE_TIME_FORMAT).timetuple())
                    res_dict['time'] = str(now)
                    res_dict['buy price'] = buy_data[coin.code]['buy_price']
                    res_dict['sell price'] = cur_price
                    res_dict['buy RSI'] = buy_data[coin.code]['buy_rsi']
                    res_dict['profit ratio'] = profit_ratio
                    res_dict['time diff'] = buy_data[coin.code]['buy_time'] - datetime.datetime.now()

                    # await static.db.insert_item_one(data=res_dict,
                    #                                 db_name='strategy_various_indicator',
                    #                                 collection_name=coin.code)
                    print('------------------------------------------')
                    # print(coin.code,' DB 삽입 완료')
                    for x in res_dict.items():
                        print(x[0],x[1])
                    print(buy_data[coin.code])   
                    print('------------------------------------------')

                    #구매기록 초기화
                    buy_data[coin.code]['buy_price'] = -1
                    buy_data[coin.code]['buy_rsi'] = -1
                    buy_data[coin.code]['buy_time'] = -1
            
            #매수 signal
            else:
                avg_volume = get_avg(df,5,'volume')[0]
                # avg_5 = get_avg(df,5)[0]
                # avg_10 = get_avg(df,10)[0]
                # avg_20 = get_avg(df,10)[0]
                
                if rsi <= 35 and df.loc[0]['volume'] < avg_volume: #and avg_5 > avg_10 > avg_20:
                    # print(coin.code,': 매수 신호, rsi : ',rsi,' 현재 거래량 : ',df.loc[0]['volume'],' 5분 평균 거래량 : ',avg_volume)

                    if buy_data[coin.code]['buy_price'] != -1:
                        continue
                    is_changed = True
                    #매수 진행
                    # print('#################매수 진행#################')
                    send_signal(coin.code,'bid',cur_price)
                    buy_data[coin.code]['buy_time'] = datetime.datetime.now()
                    buy_data[coin.code]['buy_price'] = cur_price
                    buy_data[coin.code]['buy_rsi'] = rsi
                    print('------------------------------------------')
                    print(coin.code,' 매수 후 buy_data')
                    print(buy_data[coin.code])
                    # for x in buy_data[coin.code]:
                    #     print(x[0],x[1])
                    print('------------------------------------------')