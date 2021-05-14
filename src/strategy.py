import numpy as np
import pandas as pd
import time
import pyupbit
import talib
import datetime
# import json
# import asyncio
import static
from static import log
import component
import db
import config

#목표가격을 얻는 함수 -> 금일 시가 + (전일 고가 - 전일 저가) / (0.1~1.0)
def get_target_price(coin,range_data):
    """목표가격을 얻는 함수
    Args:
        coin (str): 목표가를 구할 종목 코드
        range_data (float): 종목의 레인지 정보
    Returns:
        target: 목표가
    """
    time.sleep(0.1)
    #df = pyupbit.get_ohlcv(coin,interval='minute240',count=2)
    df = pyupbit.get_ohlcv(coin,interval='minute60',count=2)
    prio = df.iloc[-2]
    curr_open = prio['close']
    prio_high = prio['high']
    prio_low = prio['low']
    target = curr_open + (prio_high - prio_low) * range_data
    print(coin,target)
    return target

#해당 종목을 매수하는 함수
def buy_crypto_currency(coin, assigned):
    #할당된 금액에서 수수료를 제외함으로써 실제 매수금 계산
    assigned /= 1.0005
    orderbook = pyupbit.get_orderbook(coin)
    buy_price = orderbook[0]['orderbook_units'][0]['ask_price']
    unit = assigned / float(buy_price)
    static.upbit.buy_limit_order(coin, buy_price, unit)
    print('종목 : ',coin)
    print('매수 신청 가격 : ',buy_price)
    print('매수 단위 : ',unit)
    print('매수 완료!')

#해당 종목을 매도하고 총 매도금액을 리턴하는 함수
def sell_crypto_currency(coin):
    unit = static.upbit.get_balance(coin)
    orderbook = pyupbit.get_orderbook(coin)
    sell_price = orderbook[0]['orderbook_units'][0]['bid_price'] #시장가에 바로 팔 것인지
    static.upbit.sell_limit_order(coin, sell_price, unit)
    print('종목 : ',coin)
    print('매도 단위 : ',unit)
    print('판매 단가 : ',sell_price)
    print('매도 완료!')
    return sell_price, sell_price * unit * 0.9995 ###############################이게 바로 팔리나?

def get_total_ratio(res_df,range_dict,count):
    """전체 누적 수익률을 계산
    Args:
        res_df (dataFrame): 각 종목의 시간별 수익률을 저장하는 dataFrame
        range_dict (dict): 종목별 레인지를 저장하는 dict
        count (int): 투자 횟수

    Returns:
        master_df (dataFrame): 전체 누적수익률을 저장
    """
    #range별로 누적수익률 계산, 모든 종목의 누적 수익률을 저장하는 마스터 df 생성
    range_k = ['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9']
    master_df = pd.DataFrame.from_records([{'Currency':'','0.1':0.,'0.2':0.,'0.3':0.,'0.4':0.,'0.5':0.,'0.6':0.,'0.7':0.,'0.8':0.,'0.9':0.}])
    idx = 0
    for x in res_df.items():
        #종목은 해당되는 레인지만 저장하고, 전체는 모든 레인지를 보여주기 때문에 리스트를 따로 저장
        res_coin = ['누적수익률']
        res_total = [x[0]]
        for y in range_k:
            if y != str(range_dict[x[0]]):
                res_total.append('NaN') #NaN : 해당 종목에서 사용하지 않는 레인지
                continue
            tmp = []
            for k in range(count):
                #구매하지 않은 경우 연산하지 않음
                if x[1][y][k] != 'x':
                    tmp.append((x[1][y][k]+100)/100)
            #구매를 한 기록이 없으면 x 저장
            if len(tmp) == 0:
                res_coin.append('x')
                res_total.append('x')
            else:
                #누적수익률 계산
                data = (np.cumprod(tmp)[-1] - 1) * 100
                res_coin.append(data)
                res_total.append(data)
        print(res_coin)
        print(res_total)
        x[1].loc[count] = res_coin
        master_df.loc[idx] = res_total
        idx += 1
    return master_df

def volatility_breakout_strategy(range_input=None,coin_list=None):
    """변동성 돌파 전략
    Args:
        range_input (dict): {'KRW-BTC' : 0.6, 'KRW-XRP' : 0.1, 'KRW-BTT' : 0.9, ..}
        coin_list (list): ['KRW-BTC', 'KRW-XRP', 'KRW-BTT', ..]
    """
    #DB 설정
    if static.db == None:
        static.db = db.DBHandler(ip=config.MONGO['IP'],
                              port=config.MONGO['PORT'],
                              id=config.MONGO['ID'],
                              password=config.MONGO['PASSWORD'])
    
    #투자할 종목들의 coin 객체를 저장
    coin_list = [x for x in static.chart.coins.values() if x.code in coin_list]
    
    #종목별 range 설정 (입력값 제외한 나머지는 모두 0.5로 설정)
    range_dict = {x.code : 0.5 for x in coin_list if x not in range_input.keys()}
    range_dict.update(range_input)
    
    #초기 목표가 설정 (pyupbit.get_ohlcv 사용해야 하는데 비동기식으로 돌아가게 구현 못해서 0.1초 차이 발생)
    target_price = {x.code : get_target_price(x.code,range_dict[x.code]) for x in coin_list}
    
    #구매 기록 df 초기화 (구매가를 저장)
    buy_data = {x.code : -1 for x in coin_list}
    
    #투자 기록 df 초기화 (시간별 수익률 저장)
    res_df = {x.code : pd.DataFrame.from_records([{'Time':'',str(range_dict[x.code]):0}]) for x in coin_list}
    
    #투자 횟수 초기화 (몇번 투자 시도할 것인지)
    count = 0

    #투자 기간 정하기 (시간)
    #unit = 4
    unit = 1
    time_log = {x:False for x in range(0,24)}

    #원화, 종목별 초기 금액 저장
    krw = static.upbit.get_balance('KRW')
    print(krw)
    assigned_krw = {x.code : krw/len(coin_list) for x in coin_list}
    for x in assigned_krw.items():
        print(x[0],x[1])
    
    #지정 사이클만큼 투자 진행
    while count < 3:
        #지정 종목에 대해 투자
        for coin in coin_list:
            now = datetime.datetime.now()
            print('현재시간 : ',now,coin.code)
            #unit 간격으로 목표가 정하고 수익률 계산
            #if now.hour in [1,5,9,13,17,21] and time_log[now.hour] == False:
            #if time_log[now.hour] == False: #돌아가고 있는 시간대가 아닌 경우에만 실행
            if True:
                #mid = datetime.datetime(now.year, now.month, now.day, now.hour) 
                mid = datetime.datetime(now.year, now.month, now.day, now.hour,30) 
                if mid < now < mid + datetime.timedelta(seconds=1):
                    print('정보 업데이트 시작')
                    #수익률을 계산해서 해당 코인의 df에 저장
                    for coin_data in coin_list:
                        tmp = [mid]
                        cur_price = coin_data.get_trade_price()
                        if buy_data[coin_data.code] == -1:
                            tmp.append('x')
                        else: #수익률 계산 ((판매금액 / 구매 할당금액 - 1) * 100)
                            # sell_price, sell_krw = sell_crypto_currency(coin_data.code)
                            # tmp.append(((sell_krw/assigned_krw[coin_data.code])-1)*100)
                            tmp.append(((cur_price/buy_data[coin_data.code])-1)*100)
                        res_df[coin_data.code].loc[count] = tmp
                        #############################################################
                        #투자 결과를 DB에 삽입
                        res_dict = {}
                        res_dict['time'] = tmp[0]
                        res_dict['time unit'] = unit
                        if buy_data[coin_data.code] > 0:
                            res_dict['buy price'] = buy_data[coin_data.code]
                            # res_dict['sell price'] = sell_price
                            res_dict['total buy'] = assigned_krw[coin_data.code]
                            # res_dict['total sell'] = sell_krw
                            res_dict['profit ratio'] = tmp[1]
                            # res_dict['profit_KRW'] = res_dict['total sell'] - res_dict['total buy']
                        res_dict['range'] = range_dict[coin_data.code]
                        static.db.insert_item_one(data=res_dict,
                                                  db_name='strategy',
                                                  collection_name=coin_data.code)
                        #############################################################
                        print(coin_data.code,cur_price)
                    #각 코인의 목표가 갱신
                    target_price = {x.code : get_target_price(x.code,range_dict[x.code]) for x in coin_list}
                    print('구매가')
                    for x in coin_list:
                        print(x.code,buy_data[x.code])
                    
                    #각 코인의구매기록 초기화
                    buy_data = {x.code : -1 for x in coin_list}

                    #투자 횟수 + 1
                    count += 1
                    
                    #시간 기록 변경
                    time_log[now.hour] = True
                    if unit == 4 and now.hour == 1:
                        time_log[21] = False
                    else:
                        prio_hour = now.hour - unit
                        time_log[prio_hour] = False #1시일때 적용 안됨
                    print('시간 기록')
                    for x in range(0,24):
                        print(time_log[x],end=' ')
                    print('')
                    print('추가 횟수 : ',count)
                    for x in res_df.items():
                        print(x[0])
                        print(x[1])
                    time.sleep(0.5)
            #구매한 이력이 있으면 검사x
            if buy_data[coin.code] > 0:
                continue
            cur_price = coin.get_trade_price() ####################현재 호가를 orderbook[0]['orderbook_units'][0]['ask_price'] 이걸로 바꿀까? 실시간 변동이 문제인데
            if cur_price < target_price[coin.code]: #현재 호가가 목표가보다 낮으면 구매하지 않음
                continue
            else: #현재 range에서 구매 저장
                #buy_crypto_currency(coin.code, assigned_krw[coin.code])
                buy_data[coin.code] = cur_price

    #전체 누적수익률을 계산
    master_df = get_total_ratio(res_df,range_dict,count)

    #엑셀 파일에 시트 추가 (전체정보 -> 종목별 정보)
    with pd.ExcelWriter('C:\\Users\\roe96\\Desktop\\학교\\4학년\\파이썬공부\\변동성전략테스트.xlsx') as writer: # pylint: disable=abstract-class-instantiated
        master_df.to_excel(writer,sheet_name='Total',index=False)
        for x in res_df.items():
            x[1].to_excel(writer,sheet_name=x[0],index=False)
    
    for x in res_df.items():
        print(x[0])
        print(x[1])
    print('---------------------------------마스터 데이터프레임------------------------------------------')
    print(master_df)
    #exit()


# 1. DB 설정 에러
# 2. DB에 구체적 데이터 삽입 (매수, 매도를 요청하면 바로 되는게 아닌데 구체적 값을 기다렸다가 받아야 하나? (딜레이) )
# 
# 
# 






































#coin         : 종목이름
#df           : 받아온 캔들봉이 담긴 data frame
#krw          : 현재 보유 원화
#unit         : 분,일 등을 나타내는 단위
#last_candle  : df에서 가장 최근 캔들봉이 담긴 인덱스 (받아온 캔들봉 개수 -1)

#이동평균값을 구하는 함수 -> unit 동안의 주가 평균


def get_avg(df, unit=5):
    close = df['close']
    ma = close.rolling(unit).mean()
    return ma[last_candle]

#전환선, 기준선 값을 얻는 함수 -> 지정시간(last)부터 과거 unit 동안의 ( 최고가 + 최저가 ) / 2


def get_high_low_avg(df, last, unit=9):
    maxi = df.loc[last-unit+1:last, 'high']
    mini = df.loc[last-unit+1:last, 'low']

    #누락된 데이터 검사
    if maxi.isnull().any() or mini.isnull().any():
        return -1
    #최고가, 최저가를 구한 후 평균 리턴
    high = maxi.rolling(unit).max()[last]
    low = mini.rolling(unit).min()[last]
    return (high + low) / 2

#후행스팬 값을 얻는 함수 -> unit 전의 주가


def get_lagging_span(df, unit=26):
    close = df.loc[last_candle-unit, ['close']]['close']
    return close

#선행스팬1 값을 얻는 함수 -> unit 전의 ( 전환치 + 기준치 ) / 2


def get_leading_span_1(df, unit=26):
    last = last_candle - unit
    new_df = df.loc[:last]
    line_9 = get_high_low_avg(new_df, last, 9)
    line_26 = get_high_low_avg(new_df, last, 26)
    if line_9 < 0 or line_26 < 0:
        return -1
    else:
        return (line_9 + line_26) / 2

#선행스팬2 값을 얻는 함수 -> unit_1 전의 unit_2 동안의 ( 최고가 + 최저가 ) / 2


def get_leading_span_2(df, unit_1=26, unit_2=52):
    last = last_candle - unit_1
    new_df = df.loc[:last]
    maxi = new_df.loc[last-unit_2+1:last, 'high']
    mini = new_df.loc[last-unit_2+1:last, 'low']

    #누락된 데이터 검사
    if maxi.isnull().any() or mini.isnull().any():
        return -1
    #최고가, 최저가를 구한 후 평균 리턴
    high = maxi.rolling(unit_2).max()[last]
    low = mini.rolling(unit_2).min()[last]
    return (high + low) / 2

#볼린저밴드 값을 얻는 함수 -> upper, middle, lower 각각의 data frame으로 리턴


def get_bband_data(df, period=20):
    return talib.BBANDS(np.asarray(df['close']), timeperiod=period, nbdevup=2, nbdevdn=2, matype=0)

#rsi 값을 얻는 함수  -> rsi data frame을 리턴


def get_rsi_data(df, period=14):
    return talib.RSI(np.asarray(df['close']), period)

#cci 값을 얻는 함수 -> cci data frame을 리턴


def get_cci_data(df, period=14):
    return talib.CCI(df['high'], df['low'], df['close'], timeperiod=period)
