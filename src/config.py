# !/usr/bin/python
# -*- coding: utf-8 -*-
import yaml
import utils

# Upbit official fees ratio
FEES = 0.005
# KRW/BRC/ETH/USDT
FIAT = "KRW"
# Base time format
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
# Upbit time format
UPBIT_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
# Program base
PROGRAM = {
    "NAME": "Upbit Automatic Trading Program",
    "VERSION": 0.7,
    "WIDTH": 108,
    "HEIGHT": 200,
}
# Rest API request
SERVER = {
    "EXTERNAL_TIMEOUT": 60,
    "INTERNAL_TIMEOUT": 1,
    "REQUEST_LIMIT": 10,
    "PING_INTERVAL": 60
}
# Read config file
with open(utils.get_file_path('config.yaml'), 'r') as file:
    config = yaml.safe_load(file)
UPBIT = config['UPBIT']
MONGO = config['MONGO']
LOG = {
    'PATH': config['LOG']['PATH'],
    'PRINT_FORMAT': '[%(asctime)s.%(msecs)03d: %(levelname).1s %(filename)s:%(lineno)s] %(message)s',
    'SAVE': config['LOG']['SAVE'],
    'PRINT': config['LOG']['PRINT'],
}

if __name__ == '__main__':
    print(f'FEES: {FEES}')
    print(f'FIAT: {FIAT}')
    print(f'TIME_FORMAT: {TIME_FORMAT}')
    print(f'UPBIT_TIME_FORMAT: {UPBIT_TIME_FORMAT}')
    print(f'PROGRAM: {PROGRAM}')
    print(f'SERVER: {SERVER}')
    print(f'UPBIT: {UPBIT}')
    print(f'MOGNO: {MONGO}')
    print(f'LOG: {LOG}')
