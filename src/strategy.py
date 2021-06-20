from types import DynamicClassAttribute, TracebackType
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

buy_signal = []
sell_signal = []
async def test():
    # coin_list = await aiopyupbit.get_tickers(fiat="KRW")
    coin_list = ['KRW-WAVES']
    for coin in coin_list:
        time.sleep(0.1)
        signal = 0
        df = await aiopyupbit.get_ohlcv(coin,interval='minute1',count=200)
        # exit()
        df['volume_avg'] = get_avg(df,5,'volume')
        df['rsi'] = get_rsi_data(df,14)
        for x in zip(df['rsi'],df['volume'],df['volume_avg']):
            if x[0] == 'nan' or x[2] == 'nan':
                continue
            if x[0] <= 35 and x[1] < x[2]:
                signal += 1
        print(coin,' signal : ',signal)
        
    exit()
def send_buy_signal(coin,buy_price):
    buy_signal.append({'ticker':coin,'req_price':buy_price})

def send_sell_signal(coin,sell_price):
    sell_signal.append({'ticker':coin,'req_price':sell_price})

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
    #목표가 구하는 데이터를 디비에서 꺼내오면?
    df = await aiopyupbit.get_ohlcv(coin,interval='minute240',count=2)
    # df = await aiopyupbit.get_ohlcv(coin,interval='minute60',count=2)
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
    buy_res = await static.upbit.buy_limit_order(coin, buy_price, volume,contain_req=True)
    uuid = buy_res[0]['uuid']
    print('종목 : ',coin)
    print('매수 신청 가격 : ',buy_price)
    print('매수 단위 : ',volume)
    print('거래 uuid : ',uuid)
    print('남은 요청 : ',buy_res[1])
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

def get_total_ratio(res_df,count):
    """전체 누적 수익률을 계산
    Args:
        res_df (dataFrame): 각 종목의 시간별 수익률이 저장된 dataFrame
        count (int): 투자 횟수
    Returns:
        master_df (dataFrame): 전체 누적수익률이 저장된 dataFrame
    """
    #k별로 누적수익률 계산, 모든 종목의 누적 수익률을 저장하는 마스터 df 생성
    k_list = ['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9']
    master_df = pd.DataFrame.from_records([{'currency':'','0.1':0.,'0.2':0.,'0.3':0.,'0.4':0.,'0.5':0.,'0.6':0.,'0.7':0.,'0.8':0.,'0.9':0.}])
    idx = 0
    #모든 종목의 dataFrame을 탐색
    for x in res_df.items():
        #종목의 K별 누적수익률을 저장하는 리스트
        res_coin = ['누적수익률']
        #0.1~0.9의 k를 돌며 검사
        for y in k_list:
            tmp = []
            is_x = False
            #현재 K의 모든 투자 결과를 탐색하며 수익률 계산
            for k in range(count):
                print('x[1][y][k] : ',x[1][y][k])
                #구매하지 않은 경우
                if x[1][y][k] == 'x':
                    print('not buy')
                    is_x = True
                #해당 K가 아니거나, 구매에 실패했으면 NaN
                elif x[1][y][k] == 'buy delayed' or x[1][y][k] == 'NaN':
                    print('NaN의 결과')
                    continue
                #정상적으로 매매가 완료된 경우 리스트에 삽입
                else:
                    print('저장 시도')
                    tmp.append((x[1][y][k]+100)/100)

            #정상적으로 매매가 이루어진 데이터가 없는 경우
            if len(tmp) == 0:
                res = 'NaN'
                if is_x == True:
                    res = 'x'
                res_coin.append(res)
            #누적수익률 계산
            else:
                res_coin.append((np.cumprod(tmp)[-1] - 1) * 100)
        print('res coin')
        print(res_coin)
        print('x')
        print(x[0])
        print(x[1])
        print('----------------')
        #master data frame, 종목별 data frame에 계산한 누적수익률 저장
        x[1].loc[count] = res_coin
        res_coin[0] = x[0]
        master_df.loc[idx] = res_coin
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
    term = 4
    # term = 1
    term_hour = True
    term_day = False
    time_log = {x:False for x in range(0,24)}
    
    #원화, 종목별 투자 금액 저장
    krw = await static.upbit.get_balance('KRW')
    assigned_krw = {x.code : krw/len(coin_list) for x in coin_list}
    print('종목별 원화')
    for x in assigned_krw.items():
        print(x[0],x[1])
    print('----------------------------------------')
    
    #res_df에 저장하기 위한 k_list
    k_list = ['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9']
    
    # exit()
    #지정 횟수만큼 투자 진행
    while count < 5:
        #지정 종목에 대해 투자
        for coin in coin_list:
            now = datetime.datetime.now()
            print('현재시간 : ',now,end=' ')
            #term 간격으로 목표가 정하고 수익률 계산
            if now.hour in [1,5,9,13,17,21] and time_log[now.hour] == False:
            # if time_log[now.hour] == False: #돌아가고 있는 시간대가 아닌 경우에만 실행
            # if True: #테스트 코드
                mid = datetime.datetime(now.year, now.month, now.day, now.hour) #정상 코드
                # mid = datetime.datetime(now.year, now.month, now.day, now.hour,33) #테스트 코드 (검사 종료할 minute)
                if mid < now < mid + datetime.timedelta(seconds=1):
                    print('정보 업데이트 시작')
                    #수익률을 계산해서 해당 코인의 df에 저장
                    for coin_data in coin_list:
                        tmp = [mid]
                        cur_price = coin_data.get_trade_price()
                        buy_fail = False
                        profit_ratio = -1
                        
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
                                        await static.upbit.cancel_order(x['uuid'])
                                        break
                                #매수가 채결된 경우 수익률 계산 ((판매금액 / 구매 할당금액 - 1) * 100)
                                if buy_fail == True:
                                    tmp.append('buy delayed')
                                else:
                                    sell_price, sell_krw = await sell_crypto_currency(coin_data.code, buy_data[coin_data.code]['trade_volume'])
                                    profit_ratio = ((sell_krw/assigned_krw[coin_data.code])-1)*100
                                    tmp.append(profit_ratio)

                                    #tmp.append(((cur_price/buy_data[coin_data.code]['buy_price'])-1)*100)
                        
                        res_df[coin_data.code].loc[count] = tmp

                        #투자 결과를 DB에 삽입
                        res_dict = {}
                        res_dict['_id'] = time.mktime(datetime.datetime.strptime(str(tmp[0]),
                                                      static.BASE_TIME_FORMAT).timetuple())
                        res_dict['time'] = str(tmp[0])
                        res_dict['term'] = str(term)
                        if term_hour == True:
                            res_dict['term'] += ' hour'
                        elif term_day == True:
                            res_dict['term'] += ' day'
                        res_dict['k'] = k_dict[coin_data.code]

                        #매수, 매도가 이루어진 결과를 저장
                        if buy_fail == False:
                            res_dict['trade volume'] = buy_data[coin_data.code]['trade_volume']
                            res_dict['buy price'] = buy_data[coin_data.code]['buy_price']
                            res_dict['sell price'] = sell_price
                            res_dict['total buy'] = assigned_krw[coin_data.code]
                            res_dict['total sell'] = sell_krw
                            res_dict['profit ratio'] = profit_ratio
                            res_dict['profit KRW'] = res_dict['total sell'] - res_dict['total buy']
                        await static.db.insert_item_one(data=res_dict,
                                                        db_name='strategy_volatility',
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
                    print('원래 목표가')
                    for x in target_price.items():
                        print(x[0],x[1])
                    target_price = {x.code : await get_target_price(x.code,k_dict[x.code]) for x in coin_list}
                    print('new 목표가')
                    for x in target_price.items():
                        print(x[0],x[1])
                    print('----------------------------------------')
                    print('구매가, 거래량, 거래 uuid')
                    for x in coin_list:
                        print(x.code,buy_data[x.code]['buy_price'],buy_data[x.code]['trade_volume'],buy_data[x.code]['trade_uuid'])
                    
                    #각 코인의구매기록 초기화
                    buy_data = {x.code : {'buy_price' : -1, 'trade_uuid' : -1, 'trade_volume' : -1} for x in coin_list}

                    #원화, 종목별 투자 금액 저장
                    krw = await static.upbit.get_balance('KRW')
                    assigned_krw = {x.code : krw/len(coin_list) for x in coin_list}
                    print('----------------------------------------')
                    print('새로 할당된 원화')
                    for x in assigned_krw.items():
                        print(x[0],x[1])
                    print('----------------------------------------')
                    #투자 횟수 + 1
                    count += 1
                    
                    #시간 기록 변경
                    time_log[now.hour] = True
                    prio_hour = now.hour - term
                    time_log[prio_hour] = False
                    print('###############################################')
                    print('이전시간 : ',prio_hour,' 현재시간 : ',now.hour)
                    # if term == 4 and now.hour == 1:
                    #     time_log[21] = False
                    # else:
                    #     prio_hour = now.hour - term
                    #     time_log[prio_hour] = False #1시일때 적용 안됨
                    print('시간 기록')
                    for x in range(0,24):
                        print(time_log[x],end=' ')
                    print('')
                    print('###############################################')
                    print('추가 횟수 : ',count)
                    for x in res_df.items():
                        print(x[0])
                        print(x[1])
                    time.sleep(0.5)

            #매수한 이력이 있으면 검사하지 않음
            if buy_data[coin.code]['buy_price'] > 0:
                print('이미 매수')
                continue
            cur_price = coin.get_trade_price()
            
            if cur_price < target_price[coin.code]: #현재 호가가 목표가보다 낮으면 매수하지 않음
                print('목표가 도달x   현재가 : ',cur_price,'\t목표가 : ',target_price[coin.code])
                continue
            else: #현재 k에서 매수 저장
                print('목표가 도달O   현재가 : ',cur_price,'\t목표가 : ',target_price[coin.code],'매수 시도!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                trade_uuid, trade_volume = await buy_crypto_currency(coin.code, assigned_krw[coin.code], cur_price)
                buy_data[coin.code]['buy_price'] = cur_price
                buy_data[coin.code]['trade_uuid'] = trade_uuid
                buy_data[coin.code]['trade_volume'] = trade_volume
                
    #전체 누적수익률 계산
    master_df = get_total_ratio(res_df,count)

    for x in res_df.items():
        print(x[0])
        print(x[1])
    print(master_df)
    
    #엑셀 파일에 시트 추가 (전체정보 -> 종목별 정보)
    with pd.ExcelWriter('./변동성돌파전략 투자결과.xlsx') as writer: # pylint: disable=abstract-class-instantiated
        master_df.to_excel(writer,sheet_name='Total',index=False)
        for x in res_df.items():
            x[1].to_excel(writer,sheet_name=x[0],index=False)
    
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
    while True:
        for coin in coin_list:
            time.sleep(0.1)
            
            is_changed = False

            #현재가 저장
            cur_price = coin.get_trade_price()
            
            #200개의 캔들봉을 얻은 후 rsi 데이터 저장
            df = await aiopyupbit.get_ohlcv(coin.code,count = 200,interval = 'minute1')
            rsi = get_rsi_data(df, period)
            rsi = rsi[-1]

            # print(datetime.datetime.now(),'\t',int(rsi),'\t',coin.code)

            #매수 signal
            avg_volume = get_avg(df,5,'volume')[0]
            if rsi <= 35 and df.loc[0]['volume'] < avg_volume:
                # print(coin.code,': 매수 신호, rsi : ',rsi,' 현재 거래량 : ',df.loc[0]['volume'],' 5분 평균 거래량 : ',avg_volume)
                
                if buy_data[coin.code]['buy_price'] != -1:
                    continue
                is_changed = True
                #매수 진행
                # print('#################매수 진행#################')
                send_buy_signal(coin.code,cur_price)
                buy_data[coin.code]['buy_time'] = datetime.datetime.now()
                buy_data[coin.code]['buy_price'] = cur_price
                buy_data[coin.code]['buy_rsi'] = rsi
                print('------------------------------------------')
                print('매수 후 buy_data')
                print(buy_data[coin.code])
                # for x in buy_data[coin.code]:
                #     print(x[0],x[1])
                print('------------------------------------------')
            
            #매도 검사
            if buy_data[coin.code]['buy_price'] > 0:
                profit_ratio = ((cur_price/buy_data[coin.code]['buy_price'])-1)*100
                if profit_ratio >= 1 or profit_ratio <= -1:
                    # print('#################매도 진행#################')
                    is_changed = True
                    ct += 1
                    if profit_ratio >= 1:
                        plus += 1
                    else:
                        minus += 1
                    print('=======================')
                    print('투자 횟수 : ',ct)
                    print('익절 횟수 : ',plus)
                    print('손절 횟수 : ',minus)
                    print('승률 : ',plus/ct*100,'%')
                    print('=======================')
                    print('')
                    #매도 signal
                    send_sell_signal(coin.code,cur_price)

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

                    await static.db.insert_item_one(data=res_dict,
                                                    db_name='strategy_various_indicator',
                                                    collection_name=coin.code)
                    print('------------------------------------------')
                    print('DB 삽입 완료')
                    for x in res_dict.items():
                        print(x[0],x[1])
                    print('------------------------------------------')

                    #구매기록 초기화
                    buy_data[coin.code]['buy_price'] = -1
                    buy_data[coin.code]['buy_rsi'] = -1
                    buy_data[coin.code]['buy_time'] = -1
                    
            if is_changed == True:
                print('------------------------------------------')
                print('매수 시그널 리스트 길이: ',len(buy_signal))
                # for x in buy_signal:
                #     print(x)
                print('매도 시그널 리스트 길이: ',len(sell_signal))
                # for x in sell_signal:
                #     print(x)
                print('------------------------------------------')
                print('')
            # #매도 신호
            # elif rsi >= 70:
            #     print(coin.code,': 매도 신호, rsi : ',rsi)
            #     #매수 기록이 없는 경우 매도하지 않음
            #     if buy_data[coin.code]['trade_uuid'] == -1:
            #         #print('매수 기록 없음')
            #         continue
                
            #     #매수 시도를 했지만 체결이 되지 않은 경우
            #     buy_fail = False
            #     unfinished_list = await static.upbit.get_order(coin.code)
            #     for x in unfinished_list:
            #         #미체결 매수 기록이 있으면 거래를 취소
            #         if x['uuid'] == buy_data[coin.code]['trade_uuid']:
            #             buy_fail = True
            #             print('미체결 저장된 데이터')
            #             print(buy_data[coin.code])
            #             print('취소 결과')
            #             await static.upbit.cancel_order(x['uuid'])
                        
            #             #구매기록 초기화
            #             buy_data[coin.code]['buy_price'] = -1
            #             buy_data[coin.code]['trade_uuid'] = -1
            #             buy_data[coin.code]['trade_volume'] = -1                
            #             buy_data[coin.code]['buy_rsi'] = -1
                        
            #             #투자 대상 코인 개수 변경
            #             remain += 1
            #             #종목별 할당금액 업데이트
            #             krw = await static.upbit.get_balance('KRW')
            #             for x in coin_list:
            #                 if buy_data[x.code]['trade_uuid'] == -1:
            #                     assigned_krw[x.code] = krw/remain
            #             print('미체결 종목 거래 있음. 취소 후 buy_data, remain, assigned krw 업데이트 완료')
            #             print('------------------------------------------')
            #             print('새로 할당 원화')
            #             for x in assigned_krw.items():
            #                 print(x[0],x[1])
            #             print('------------------------------------------')
            #             print('미체결 취소 후 buy_data')
            #             for x in buy_data.items():
            #                 print(x[0],x[1])
            #             print('------------------------------------------')       
            #             print('투자 대상 종목 수 : ',remain)
            #             print('------------------------------------------')
            #             break
            #     #매수 기록이 있고 미체결인 경우 매도하지 않음
            #     if buy_fail == True:
            #         print('매수 기록 미체결')
            #         continue
            #     print('#################매도 진행#################')
            #     sell_price, sell_krw = await sell_crypto_currency(coin.code, buy_data[coin.code]['trade_volume'])
            #     # profit_ratio = ((sell_krw/6000)-1)*100
            #     profit_ratio = ((sell_krw/assigned_krw[coin.code])-1)*100
                
            #     #투자 결과를 DB에 삽입
            #     res_dict = {}
            #     now = datetime.datetime.now()
            #     now = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
            #     res_dict['_id'] = time.mktime(datetime.datetime.strptime(str(now),
            #                                   static.BASE_TIME_FORMAT).timetuple())
            #     res_dict['time'] = str(now)
            #     res_dict['trade volume'] = buy_data[coin.code]['trade_volume']
            #     res_dict['buy price'] = buy_data[coin.code]['buy_price']
            #     res_dict['sell price'] = sell_price
            #     res_dict['total buy'] = assigned_krw[coin.code]
            #     res_dict['total sell'] = sell_krw
            #     res_dict['profit ratio'] = profit_ratio
            #     res_dict['profit KRW'] = res_dict['total sell'] - res_dict['total buy']
            #     res_dict['buy RSI'] = buy_data[coin.code]['buy_rsi']
            #     res_dict['sell RSI'] = rsi
                
            #     await static.db.insert_item_one(data=res_dict,
            #                                     db_name='strategy_rsi',
            #                                     collection_name=coin.code)
            #     print('------------------------------------------')
            #     print('DB 삽입 완료')
            #     for x in res_dict.items():
            #         print(x[0],x[1])
            #     print('------------------------------------------')
            #     #구매기록 초기화
            #     buy_data[coin.code]['buy_price'] = -1
            #     buy_data[coin.code]['trade_uuid'] = -1
            #     buy_data[coin.code]['trade_volume'] = -1                
            #     buy_data[coin.code]['buy_rsi'] = -1

            #     #투자 대상 코인 개수 변경
            #     remain += 1
                
            #     #종목별 할당금액 업데이트
            #     krw = await static.upbit.get_balance('KRW')
            #     for x in coin_list:
            #         if buy_data[x.code]['trade_uuid'] == -1:
            #             assigned_krw[x.code] = krw/remain
            #     print('------------------------------------------')
            #     print('새로 할당 원화')
            #     for x in assigned_krw.items():
            #         print(x[0],x[1])
            #     print('------------------------------------------')
            #     print('매도 후 buy_data')
            #     for x in buy_data.items():
            #         print(x[0],x[1])
            #     print('------------------------------------------')
            #     print('투자 대상 종목 수 : ',remain)
            #     print('------------------------------------------')
                
# 20 매수 80 매도 : 너무 욕심같음 80전에 최고점 찍고 내려와버려서 오히려 손해나는 경우가 있음
# 20 매수 70 매도 : 실험중



#coin         : 종목이름
#df           : 받아온 캔들봉이 담긴 data frame
#krw          : 현재 보유 원화
#unit         : 분,일 등을 나타내는 단위
#last_candle  : df에서 가장 최근 캔들봉이 담긴 인덱스 (받아온 캔들봉 개수 -1)

#이동평균값을 구하는 함수 -> unit 동안의 평균
def get_avg(df, unit=5,column='close'):
    return df[column].rolling(unit).mean()
    # return ma[last_candle]
    
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