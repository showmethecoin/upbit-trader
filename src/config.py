# !/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import yaml
import utils


class Config:
    def __init__(self,
                 mongo_ip: str = '127.0.0.1',
                 mongo_port: int = 27017,
                 mongo_id: str = 'root',
                 mongo_password: str = 'qwe123',
                 log_path: str = 'upbit-trader.log',
                 log_save: bool = False,
                 log_print: bool = True,
                 log_format: str = '[%(asctime)s.%(msecs)03d: %(levelname).1s %(filename)s:%(lineno)s] %(message)s'):
        self.upbit_access_key = None
        self.upbit_secret_key = None

        self.mongo_ip = mongo_ip
        self.mongo_port = mongo_port
        self.mongo_id = mongo_id
        self.mongo_password = mongo_password

        if log_path == 'upbit-trader.log' and not sys.platform.startswith('win'):
            self.log_path = '~/.upbit-trader.log'
        else:
            self.log_path = log_path
        self.log_save = log_save
        self.log_print = log_print
        self.log_format = log_format

        self.program_version = 0.7

    def to_dict(self) -> dict:
        config = {}
        config['UPBIT'] = {}
        config['UPBIT']['ACCESS_KEY'] = self.upbit_access_key
        config['UPBIT']['SECRET_KEY'] = self.upbit_secret_key
        config['MONGO'] = {}
        config['MONGO']['IP'] = self.mongo_ip
        config['MONGO']['PORT'] = self.mongo_port
        config['MONGO']['ID'] = self.mongo_id
        config['MONGO']['PASSWORD'] = self.mongo_password
        config['LOG'] = {}
        config['LOG']['PATH'] = self.log_path
        config['LOG']['SAVE'] = self.log_save
        config['LOG']['PRINT'] = self.log_print
        config['LOG']['FORMAT'] = self.log_format
        return config

    def load(self) -> dict:
        try:
            with open(utils.get_file_path('config.yaml'), 'r') as file:
                config = yaml.safe_load(file)
                if 'UPBIT' in config:
                    self.upbit_access_key = config['UPBIT']['ACCESS_KEY']
                    self.upbit_secret_key = config['UPBIT']['SECRET_KEY']
                if 'MONGO' in config:
                    self.mongo_ip = config['MONGO']['IP']
                    self.mongo_port = config['MONGO']['PORT']
                    self.mongo_id = config['MONGO']['ID']
                    self.mongo_password = config['MONGO']['PASSWORD']
                if 'LOG' in config:
                    self.log_path = config['LOG']['PATH']
                    self.log_save = config['LOG']['SAVE']
                    self.log_print = config['LOG']['PRINT']
        except FileNotFoundError:
            self.save(self.to_dict())

    def save(self) -> bool:
        with open(utils.get_file_path('config.yaml'), 'w') as file:
            return yaml.safe_dump(self.to_dict(), file)


if __name__ == '__main__':
    import pprint
    import static
    static.config = Config()
    static.config.load()
    pprint.pprint(static.config.to_dict())
