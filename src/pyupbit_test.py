import pandas as pd
import pyupbit
import datetime
import time
import pymongo
from pymongo import MongoClient
from pymongo.cursor import CursorType
#db 연결
host = "codejune.iptime.org"
port = "27017"
client = MongoClient('mongodb://root:qwe123@codejune.iptime.org:27017')
db = client.younghoon_test
coins = pyupbit.get_tickers()
all_coin = pyupbit.get_tickers()
coins = [x for x in all_coin if x.split('-')[0] == 'KRW']
collection = [db[x] for x in coins]
target_price = {}

#업비트 로그인
access = ""
secret = ""
upbit = pyupbit.Upbit(access, secret)

#목표가격을 얻는 함수


def get_target_price(coin):
    df = pyupbit.get_ohlcv(coin)
    prio = df.iloc[-2]
    curr_open = prio['close']
    prio_high = prio['high']
    prio_low = prio['low']
    target = curr_open + (prio_high - prio_low) * 0.5
    return target

#입력한 분단위의 평균값을 구하는 함수


def get_avg(df, min=5):
    close = df['close']
    ma = close.rolling(min).mean()
    return ma[19]

#해당 종목을 매수하는 함수


def buy_crypto_currency(coin):
    orderbook = pyupbit.get_orderbook(coin)
    sell_price = orderbook[0]['orderbook_units'][0]['ask_price']
    unit = krw/float(sell_price)
    print('=====================================')
    print('종목 : ', coin)
    print('목표가 : ', target_price[coin])
    print('현재가 : ', price)
    print('매수 신청 가격 : ', sell_price)
    print('매수 단위 : ', unit)
    print('모의 매수 완료!')
    #주석 지우면 실제로 매수됨
    #upbit.buy_limit_order(coin, sell_price, unit)

#해당 종목을 매도하는 함수


def sell_crypto_currency(coin):
    unit = upbit.get_balance(coin)
    upbit.sell_market_order(coin, unit)

#후행스팬 값을 얻는 함수


def get_lagging_span(coin, min=26):
    prio = now-datetime.timedelta(minutes=min)
    prio = prio.strftime('%Y-%m-%d %H:%M:00')
    prio = pd.to_datetime(prio)
    test_query = {'time': {'$in': [prio]}}
    ret = client['younghoon_test'][coin].find_one(test_query, {"_id": False})
    if ret == None:
        return -1
    else:
        print("후행스팬 : ", prio, " ", ret['close'], " 값과 비교")
        return ret['close']


#초기 타겟 가격 저장 (안하면 정각에 첫 데이터 저장될때까지 기다려야함..)
for coin in coins:
    res = get_target_price(coin)
    #목표가 dictionary에 저장
    target_price[coin] = res
    print(coin, '\t\ttarget price : ', res)
    time.sleep(0.2)

now = datetime.datetime.now()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
while True:
    now = datetime.datetime.now()
    #정각인 경우에만 목표가를 계산해서 저장
    if mid < now < mid + datetime.timedelta(seconds=10):
        print(now)
        for coin in coins:
            res = get_target_price(coin)
            #목표가 dictionary에 저장
            target_price[coin] = res
            print(coin, '\t\ttarget price : ', res)
            time.sleep(0.2)
        #새로운 정각시간 계산
        mid = datetime.datetime(now.year, now.month,
                                now.day) + datetime.timedelta(1)
        sell_crypto_currency(coin)
    #현재 원화 보유량 저장
    krw = upbit.get_balance('KRW')
    #모든 종목에 대해서 디비에 데이터를 저장하며 매수 검사(가격이 높을때에만) → 다중 쓰레드를 써야할듯. 1분안에 안끝나
    for coin in coins:
        now = datetime.datetime.now()
        print('-----------------------------------------')
        print(coin, " 종목 테스트")
        #20개 캔들봉을 받아와서 dictionary list로 변경. 마지막 데이터는 변동중이므로 저장하지 않음
        items_df = pyupbit.get_ohlcv(ticker=coin, interval="minute1", count=20)
        items_df = items_df.reset_index()
        items_df = items_df.rename({'index': 'time'}, axis='columns')

        #19개의 캔들봉 데이터를 중복검사 후에 저장
        tmp = [items_df.loc[i, :].to_dict() for i in range(len(items_df)-1)]
        items = []

        for i in tmp:
            query = {'time': {'$in': [i['time']]}}
            ret = client['younghoon_test'][coin].find_one(
                query, {"_id": False})
            #중복이면 insert하지 않음
            if ret == None:
                items.append(i)
        for i in items:
            print(i['time'], " 추가 완료")
        if items:
            client['younghoon_test'][coin].insert_many(
                items).inserted_ids  # insert_item_many 함수로 대체

        #현 시점에서 5분,10분,20분 평균값 구하기
        avg_5 = get_avg(items_df, 5)
        avg_10 = get_avg(items_df, 10)
        avg_20 = get_avg(items_df, 20)
        print('5분평균 : ', avg_5)
        print('10분평균 : ', avg_10)
        print('20분평균 : ', avg_20)
        #골든크로스 검사
        if avg_5 > avg_10 and avg_5 > avg_20:
            lag_span = get_lagging_span(coin, min=26)
            price = pyupbit.get_current_price(coin)
            #후행스팬 검사
            if lag_span > 0 and price > lag_span:
                #목표가 도달 검사
                if price > target_price[coin]:
                    #매수 실행
                    buy_crypto_currency(coin)
                    krw = upbit.get_balance('KRW')
        time.sleep(0.2)
