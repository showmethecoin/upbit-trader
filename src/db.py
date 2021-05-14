# !/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import motor.motor_asyncio
from pymongo import CursorType

class DBHandler:
    """MongoDB 핸들러
    """

    def __init__(self,
                 ip='localhost', 
                 port=27017, 
                 id=None, 
                 password=None, loop=None):
        self.ip = ip
        self.port = port
        self.id = id
        self.password = password
        self.host = f'mongodb://{self.id}:{self.password}@{self.ip}:{self.port}'
        if loop:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                self.host, io_loop=loop)
            self.loop = loop
        else:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.host)

    async def insert_item_one(self, data: dict = None, db_name: str = None, collection_name: str = None) -> bool:
        """도큐멘트 1개 저장

        Args:
            data (dict, optional): DB에 저장할 도큐먼트 데이터 딕셔너리. Defaults to None.
            db_name (str, optional): DB 이름. Defaults to None.
            collection_name (str, optional): Collection 이름. Defaults to None.

        Returns:
            bool: [description]
        """
        return True if await self.client[db_name][collection_name].insert_one(data).inserted_id else False

    async def insert_item_many(self, data: list = None, db_name: str = None, collection_name: str = None, ordered: bool = False) -> list:
        """도큐먼트 N개 저장

        Args:
            data (list, optional): DB에 저장할 도큐먼트 데이터 딕셔너리 리스트. Defaults to None.
            db_name (str, optional): DB 이름. Defaults to None.
            collection_name (str, optional): Collection 이름. Defaults to None.
            ordered (bool, optional): 데이터 순서대로 삽입 여부(중복 처리 여부). Defaults to False.

        Returns:
            None: [description]
        """

        result = await self.client[db_name][collection_name].insert_many(documents=data, ordered=ordered)
        return result.inserted_ids

    async def find_item_one(self, condition: dict = None, db_name: str = None, collection_name: str = None) -> dict:
        """도큐먼트 한개 추출

        Args:
            condition (dict, optional): 추출할 데이터 조건식. Defaults to None.
            db_name (str, optional): DB 이름. Defaults to None.
            collection_name (str, optional): Collection 이름. Defaults to None.

        Returns:
            dict: [description]
        """
        result = await self.client[db_name][collection_name].find_one(condition, {"_id": False})
        return result.inserted_id

    async def find_item(self, condition: dict = None, db_name: str = None, collection_name: str = None):
        return self.client[db_name][collection_name].find(condition, {"_id": False}, no_cursor_timeout=True, cursor_type=CursorType.EXHAUST)

    async def delete_item_one(self, condition: dict = None, db_name: str = None, collection_name: str = None):
        return await self.client[db_name][collection_name].delete_one(condition)

    async def delete_item_many(self, condition: dict = None, db_name: str = None, collection_name: str = None):
        return await self.client[db_name][collection_name].delete_many(condition)

    async def update_item_one(self, condition: dict = None, update_value=None, db_name: str = None, collection_name: str = None):
        return await self.client[db_name][collection_name].update_one(filter=condition, update=update_value)

    async def update_item_many(self, condition: dict = None, update_value=None, db_name: str = None, collection_name: str = None):
        return await self.client[db_name][collection_name].update_many(filter=condition, update=update_value)

    async def text_search(self, text=None, db_name: str = None, collection_name: str = None):
        return self.client[db_name][collection_name].find({"$text": {"$search": text}})


async def main():
    db = DBHandler(ip=static.config.mongo_ip, port=static.config.mongo_port,
                   id=static.config.mongo_id, password=static.config.mongo_password)

    # MongoDB에서 데이터 추출(내림차순)
    data = await db.find_item(condition=None, db_name='candles',
                              collection_name='KRW-ADA_minute_1')
    data = data.sort('time', -1)

    data_df = pd.DataFrame(await data.to_list(length=None))
    # Dataframe 인덱스 설정
    data_df['time'] = pd.to_datetime(data_df['time'])
    data_df = data_df.set_index('time', inplace=False)

    # Dataframe 리샘플링
    RESAMPLING = 'B'
    new_df = pd.DataFrame()
    new_df['open'] = data_df.open.resample(RESAMPLING).first()
    new_df['high'] = data_df.high.resample(RESAMPLING).max()
    new_df['low'] = data_df.low.resample(RESAMPLING).min()
    new_df['close'] = data_df.close.resample(RESAMPLING).last()
    new_df['volume'] = data_df.volume.resample(RESAMPLING).sum()
    new_df = new_df.sort_index(ascending=True)

    print(new_df)

if __name__ == '__main__':
    import asyncio
    import static
    import config
    
    static.config = config.Config()
    static.config.load()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
