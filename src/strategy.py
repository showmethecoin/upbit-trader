import numpy as np
import pandas as pd
import time
import aiopyupbit
import talib
import datetime
import asyncio

import component
import db
import config
import static
from static import log

from db import DBHandler

async def get_best_k(coin):
    """백테스팅을 통해 최적의 k를 찾는 함수
    Args:
        coin (str): k를 얻을 종목 코드
    Returns:
        백테스팅을 통해 찾은 최적의 k
    """
    time.sleep(0.1)
    df = await aiopyupbit.get_ohlcv(coin,interval='minute60',count=20)
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
    #목표가 구하는 데이터를 디비에서 꺼내오면? -> 데이터가 디비에 없을 수도 있는데?
    # df = await aiopyupbit.get_ohlcv(coin,interval='minute240',count=2)
    df = await aiopyupbit.get_ohlcv(coin,interval='minute60',count=2)
    prio = df.iloc[-2]
    curr_open = prio['close']
    prio_high = prio['high']
    prio_low = prio['low']
    target = curr_open + (prio_high - prio_low) * k_data
    print(coin,target)
    return target

#해당 종목을 매수하는 함수
async def buy_crypto_currency(coin, assigned, buy_price):
    """지정가로 종목을 매수하는 함수
    Args:
        coin (str): 매수할 종목 코드
        assigned (float): 종목을 매수하는데 할당된 원화
        buy_price (float): 종목을 매수할 가격
    Returns:
        uuid (str): 매수를 신청한 거래의 uuid
        volume (float): 매수를 신청한 수량
    """
    #할당된 금액에서 수수료를 제외함으로써 실제 매수금 계산
    # orderbook = await aiopyupbit.get_orderbook(coin)
    # buy_price = orderbook[0]['orderbook_units'][0]['ask_price']
    assigned /= 1.0005
    volume = assigned / float(buy_price)
    uuid = (await static.upbit.buy_limit_order(coin, buy_price, volume))['uuid']
    print('종목 : ',coin)
    print('매수 신청 가격 : ',buy_price)
    print('매수 단위 : ',volume)
    print('거래 uuid : ',uuid)
    print('매수 완료!')
    return uuid, volume

#해당 종목을 매도하고 총 매도금액을 리턴하는 함수
async def sell_crypto_currency(coin, volume):
    """시장가로 종목을 매도하는 함수
    Args:
        coin (str): 매도할 종목 코드
        volume (float): 매도할 수량
    Returns:
        sell_price (float): 종목을 매도한 가격
        sell_krw (float): 수수료를 제외한 총 매도 금액
    """
    orderbook = await aiopyupbit.get_orderbook(coin)
    sell_price = orderbook[0]['orderbook_units'][0]['bid_price'] #일단은 시장가로 판매
    await static.upbit.sell_limit_order(coin, sell_price, volume)
    sell_krw = sell_price * volume * 0.9995
    print('종목 : ',coin)
    print('매도 단위 : ',volume)
    print('판매 단가 : ',sell_price)
    print('매도 완료!')
    return sell_price, sell_krw ###############################이게 바로 팔리나?

def get_total_ratio(res_df,k_dict,count):
    """전체 누적 수익률을 계산
    Args:
        res_df (dataFrame): 각 종목의 시간별 수익률을 저장하는 dataFrame
        k_dict (dict): 종목별 레인지를 저장하는 dict
        count (int): 투자 횟수
    Returns:
        master_df (dataFrame): 전체 누적수익률을 저장
    """
    #k별로 누적수익률 계산, 모든 종목의 누적 수익률을 저장하는 마스터 df 생성
    k_list = ['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9']
    master_df = pd.DataFrame.from_records([{'currency':'','0.1':0.,'0.2':0.,'0.3':0.,'0.4':0.,'0.5':0.,'0.6':0.,'0.7':0.,'0.8':0.,'0.9':0.}])
    idx = 0
    for x in res_df.items():
        #종목은 해당되는 레인지만 저장하고, 전체는 모든 레인지를 보여주기 때문에 리스트를 따로 저장
        res_coin = ['누적수익률']
        res_total = [x[0]]
        for y in k_list:
            flag = True
            for z in x[1][y]:
                if z != 'NaN' and x[1]['Time'][0] != '':
                    flag = False
                    break
            if flag == True:
                res_total.append('NaN')
                res_coin.append('NaN')
                continue
            tmp = []
            for k in range(count):
                #구매하지 않은 경우 연산하지 않음
                if x[1][y][k] != 'x' and x[1][y][k] != 'fail':
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
        print('res coin')
        print(res_coin)
        print('res total')
        print(res_total)
        print('x')
        print(x[0])
        print(x[1])
        print('----------------')
        x[1].loc[count] = res_coin
        master_df.loc[idx] = res_total
        idx += 1
    return master_df

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
    print('목표가')
    target_price = {x.code : await get_target_price(x.code,k_dict[x.code]) for x in coin_list}
    print('----------------------------------------')
    print('K값')
    for x in k_dict.items():
        print(x[0],x[1])
    print('----------------------------------------')
    
    #구매 기록 df 초기화 (구매 정보를 저장)
    buy_data = {x.code : {'buy_price' : -1, 'trade_uuid' : -1, 'trade_volume' : -1} for x in coin_list}
    
    #투자 기록 df 초기화 (시간별 수익률 저장)
    res_df = {x.code : pd.DataFrame.from_records([{'Time':'','0.1':'','0.2':'','0.3':'','0.4':'','0.5':'','0.6':'','0.7':'','0.8':'','0.9':''}]) for x in coin_list}
    
    #투자 횟수 초기화 (몇번 투자 시도할 것인지)
    count = 0

    #투자 기간 정하기 (시간)
    # unit = 4
    unit = 1
    time_log = {x:False for x in range(0,24)}
    
    #원화, 종목별 초기 금액 저장
    krw = await static.upbit.get_balance('KRW')
    assigned_krw = {x.code : krw/len(coin_list) for x in coin_list}
    print('종목별 원화')
    for x in assigned_krw.items():
        print(x[0],x[1])
    print('----------------------------------------')
    
    #res_df에 저장하기 위한 k_list
    k_list = ['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9']
    
    # exit()
    #지정 사이클만큼 투자 진행
    while count < 0:
        #지정 종목에 대해 투자
        for coin in coin_list:
            now = datetime.datetime.now()
            print('현재시간 : ',now)
            #unit 간격으로 목표가 정하고 수익률 계산
            #if now.hour in [1,5,9,13,17,21] and time_log[now.hour] == False:
            # if time_log[now.hour] == False: #돌아가고 있는 시간대가 아닌 경우에만 실행
            if True: #테스트 코드
                # mid = datetime.datetime(now.year, now.month, now.day, now.hour) #정상 코드
                mid = datetime.datetime(now.year, now.month, now.day, now.hour,9) #테스트 코드 (검사 종료할 minute)
                if mid < now < mid + datetime.timedelta(seconds=1):
                    print('정보 업데이트 시작')
                    #수익률을 계산해서 해당 코인의 df에 저장
                    for coin_data in coin_list:
                        tmp = [mid]
                        cur_price = coin_data.get_trade_price()
                        buy_fail = False

                        #k를 반올림해서 res_df에 저장
                        tmp_k = round(k_dict[coin_data.code],1)
                        if tmp_k >= 1 :
                            tmp_k = 0.9
                        elif tmp_k <= 0 :
                            tmp_k = 0.1
                        print('원래 : ',k_dict[coin_data.code])
                        print('반올림 : ',tmp_k)
                        for k in k_list:
                            #현재 k에 대해서만 진행
                            if k != str(tmp_k):
                                print('검사 k : ',k,' 현재 k 아님')
                                tmp.append('NaN')
                                continue
                            #매수하지 않은 경우
                            if buy_data[coin_data.code]['buy_price'] == -1:
                                print('매수 x')
                                tmp.append('x')
                                buy_fail = True
                            else:
                                #매수 시도를 했지만 체결이 되지 않은 경우
                                for x in await static.upbit.get_order(coin_data.code):
                                    if x['uuid'] == buy_data[coin_data.code]['trade_uuid']:
                                        buy_fail = True
                                        static.upbit.cancel_order(x['uuid'])
                                        break
                                #매수가 채결된 경우 수익률 계산 ((판매금액 / 구매 할당금액 - 1) * 100)
                                if buy_fail == True:
                                    tmp.append('buy delayed')
                                else:
                                    sell_price, sell_krw = await sell_crypto_currency(coin_data.code, buy_data[coin_data.code]['trade_volume'])
                                    tmp.append(((sell_krw/assigned_krw[coin_data.code])-1)*100)
                                    #tmp.append(((cur_price/buy_data[coin_data.code]['buy_price'])-1)*100)
                        
                        res_df[coin_data.code].loc[count] = tmp

                        #투자 결과를 DB에 삽입
                        print('buy_fail : ',buy_fail)
                        res_dict = {}
                        print(now,mid)
                        print('---------------------------------------')
                        res_dict['_id'] = time.mktime(datetime.datetime.strptime(str(tmp[0]), static.BASE_TIME_FORMAT).timetuple())
                        res_dict['time'] = str(tmp[0])
                        res_dict['time unit'] = unit
                        res_dict['k'] = k_dict[coin_data.code]
                        if buy_fail == False:
                            res_dict['trade volume'] = buy_data[coin_data.code]['trade_volume']
                            res_dict['buy price'] = buy_data[coin_data.code]['buy_price']
                            res_dict['sell price'] = sell_price
                            res_dict['total buy'] = assigned_krw[coin_data.code]
                            res_dict['total sell'] = sell_krw
                            res_dict['profit ratio'] = tmp[1]
                            res_dict['profit KRW'] = res_dict['total sell'] - res_dict['total buy']
                        await static.db.insert_item_one(data=res_dict,
                                                        db_name='strategy',
                                                        collection_name=coin_data.code)
                    
                    #종목별 k 갱신 (입력값 제외한 나머지는 백테스팅을 통해 설정)
                    print('----------------------------------------')
                    print('원래 K값')
                    for x in k_dict.items():
                        print(x[0],x[1])
                    k_dict = {x.code : await get_best_k(x.code) for x in coin_list if x not in k_input.keys()}
                    k_dict.update(k_input)
                    print('바뀐 K값')
                    for x in k_dict.items():
                        print(x[0],x[1])
                    print('----------------------------------------')
                    #각 코인의 목표가 갱신
                    print('목표가')
                    target_price = {x.code : await get_target_price(x.code,k_dict[x.code]) for x in coin_list}
                    print('----------------------------------------')
                    print('구매가, 거래량, 거래 uuid')
                    for x in coin_list:
                        print(x.code,buy_data[x.code]['buy_price'],buy_data[x.code]['trade_volume'],buy_data[x.code]['trade_uuid'])
                    
                    #각 코인의구매기록 초기화
                    buy_data = {x.code : {'buy_price' : -1, 'trade_uuid' : -1, 'trade_volume' : -1} for x in coin_list}

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

            #매수한 이력이 있으면 검사하지 않음
            if buy_data[coin.code]['buy_price'] > 0:
                continue
            cur_price = coin.get_trade_price()
            # print(cur_price)
            if cur_price < target_price[coin.code]: #현재 호가가 목표가보다 낮으면 매수하지 않음
                continue
            else: #현재 k에서 매수 저장
                trade_uuid, trade_volume = await buy_crypto_currency(coin.code, assigned_krw[coin.code], cur_price)
                buy_data[coin.code]['buy_price'] = cur_price
                buy_data[coin.code]['trade_uuid'] = trade_uuid
                buy_data[coin.code]['trade_volume'] = trade_volume
                
    #전체 누적수익률 계산
    master_df = get_total_ratio(res_df,k_dict,count)

    for x in res_df.items():
        print(x[0])
        print(x[1])
    print('---------------------------------마스터 데이터프레임------------------------------------------')
    print(master_df)
    
    #엑셀 파일에 시트 추가 (전체정보 -> 종목별 정보)
    with pd.ExcelWriter('./변동성전략테스트.xlsx') as writer: # pylint: disable=abstract-class-instantiated
        master_df.to_excel(writer,sheet_name='Total',index=False)
        for x in res_df.items():
            x[1].to_excel(writer,sheet_name=x[0],index=False)
    
    exit()
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

# if __name__ == '__strategy__':
#     static.config = config.Config()
#     static.config.load()
#     static.upbit = aiopyupbit.Upbit(static.config.upbit_access_key, static.config.upbit_secret_key)
#     # loop = asyncio.new_event_loop()
#     # asyncio.set_event_loop(loop)




# 투자 한번 끝날때마다 레인지 변경. 
# 레인지가 바뀐다면 res_df에 바뀐 레인지값의 이전 정보를 NaN으로 저장
# 그리고 레인지 0일때 0 말고 다른식으로 저장



