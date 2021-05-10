import numpy as np
import pyupbit
import talib
#coin         : 종목이름
#df           : 받아온 캔들봉이 담긴 data frame
#krw          : 현재 보유 원화
#unit         : 분,일 등을 나타내는 단위
#last_candle  : df에서 가장 최근 캔들봉이 담긴 인덱스 (받아온 캔들봉 개수 -1)

#해당 종목을 매수하는 함수


def buy_crypto_currency(coin):
    orderbook = pyupbit.get_orderbook(coin)
    sell_price = orderbook[0]['orderbook_units'][0]['ask_price']
    unit = krw / float(sell_price)
    upbit.buy_limit_order(coin, sell_price, unit)
    print('종목 : ', coin)
    print('매수 신청 가격 : ', sell_price)
    print('매수 단위 : ', unit)
    print('매수 완료!')

#해당 종목을 매도하는 함수


def sell_crypto_currency(coin):
    unit = upbit.get_balance(coin)
    upbit.sell_market_order(coin, unit)
    print('종목 : ', coin)
    print('매도 단위 : ', unit)
    print('매도 완료!')

#목표가격을 얻는 함수 -> 금일 시가 + (전일 고가 - 전일 저가) / 2


def get_target_price(coin):
    df = pyupbit.get_ohlcv(coin, count=2)
    prio = df.iloc[-2]
    curr_open = prio['close']
    prio_high = prio['high']
    prio_low = prio['low']
    target = curr_open + (prio_high - prio_low) * 0.5
    return target

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
