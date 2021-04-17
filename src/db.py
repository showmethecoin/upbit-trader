import pandas as pd
from pymongo import MongoClient
from pymongo import CursorType

import config


class DBHandler:
    """MongoDB 핸들러
    """

    def __init__(self, ip='localhost', port=27017, id=None, password=None):
        self.ip = ip
        self.port = port
        self.id = id
        self.password = password
        self.host = f'mongodb://{self.id}:{self.password}@{self.ip}:{self.port}'
        self.client = MongoClient(self.host)

    def insert_item_one(self, data: dict = None, db_name: str = None, collection_name: str = None) -> bool:
        """도큐멘트 1개 저장

        Args:
            data (dict, optional): DB에 저장할 도큐멘트 데이터. Defaults to None.
            db_name (str, optional): DB 이름. Defaults to None.
            collection_name (str, optional): Collection 이름. Defaults to None.

        Returns:
            bool: [description]
        """
        return True if self.client[db_name][collection_name].insert_one(data).inserted_id else False

    def insert_item_many(self, data=None, db_name=None, collection_name=None, ordered=False):
        result = self.client[db_name][collection_name].insert_many(
            documents=data, ordered=ordered).inserted_ids
        return result

    def find_item_one(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find_one(condition, {
                                                                "_id": False})
        return result

    def find_item(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find(
            condition, {"_id": False}, no_cursor_timeout=True, cursor_type=CursorType.EXHAUST)
        return result

    def delete_item_one(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].delete_one(condition)
        return result

    def delete_item_many(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].delete_many(condition)
        return result

    def update_item_one(self, condition=None, update_value=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].update_one(
            filter=condition, update=update_value)
        return result

    def update_item_many(self, condition=None, update_value=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].update_many(
            filter=condition, update=update_value)
        return result

    def text_search(self, text=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find(
            {"$text": {"$search": text}})
        return result


if __name__ == '__main__':

    db = DBHandler(ip=config.DB['IP'], port=config.DB['PORT'],
                   id=config.DB['ID'], password=config.DB['PASSWORD'])

    # MongoDB에서 데이터 추출(내림차순)
    data = db.find_item(condition=None, db_name='candles', collection_name='KRW-ADA_minute_1').sort('time', -1)

    data_df = pd.DataFrame(list(data))
    # Dataframe 인덱스 설정
    data_df['time'] = pd.to_datetime(data_df['time'])
    data_df = data_df.set_index('time', inplace=False)

    # Dataframe 리샘플링
    RESAMPLING = '5T'
    new_df = pd.DataFrame()
    new_df['open'] = data_df.open.resample(RESAMPLING).first()
    new_df['high'] = data_df.high.resample(RESAMPLING).max()
    new_df['low'] = data_df.low.resample(RESAMPLING).min()
    new_df['close'] = data_df.close.resample(RESAMPLING).last()
    new_df['volume'] = data_df.volume.resample(RESAMPLING).sum()
    new_df = new_df.sort_index(ascending=True)

    print(new_df)

