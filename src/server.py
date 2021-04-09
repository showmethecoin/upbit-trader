import pyupbit
from pymongo import MongoClient, CursorType
from db import DBHandler
import config
import time

if __name__ == '__main__':

    db = DBHandler(ip=config.DB['IP'], port=config.DB['PORT'], id=config.DB['ID'], password=config.DB['PASSWORD'])
    while True:
        items_df = pyupbit.get_ohlcv(ticker="KRW-BTC", interval="minute1", count=10)
        items = [items_df.loc[i,:].to_dict() for i in range(len(items_df))]
        for i in items:
            query = {'time':{'$in':[i['time']]}}
            ret = db.find_item_one(condition=query, db_name='history', collection_name='KRW_BTC')
            if ret != None:
                print(ret)
            else:
                db.insert_item_one(data=i, db_name='history', collection_name='KRW_BTC')
            
        time.sleep(1)

        """for i in static.chart.codes:
            static.chart.coins[i].candle_result = False
        asyncio.run(static.chart.get_candles(0))
        asyncio.run(static.chart.get_candles(1))"""