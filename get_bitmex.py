# IMPORTS
import pandas as pd
import math
import os.path
import time
from bitmex import bitmex
import numpy as np
import tulipy as ti

# from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
from dateutil.tz import tzutc
from tqdm import tqdm_notebook #(Optional, used for progress-bars)

### API
from tools_bitmex import get_mean_open_close

bitmex_api_key = "hN5B4AR9ZzChK7X3phriTH5S"    #Enter your own API-key here
bitmex_api_secret = "NHtP7ZyhkjgylTtB5-AsPxlVJ7tngw64JYYzs3JZw_1qvuot" #Enter your own API-secret here
binance_api_key = '[REDACTED]'    #Enter your own API-key here
binance_api_secret = '[REDACTED]' #Enter your own API-secret here

### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
batch_size = 750
bitmex_client = bitmex(test=False, api_key=bitmex_api_key, api_secret=bitmex_api_secret)
# binance_client = Client(api_key=binance_api_key, api_secret=binance_api_secret)



### FUNCTIONS
def minutes_of_new_data(symbol, kline_size, data, source):
    if len(data) > 0:  old = parser.parse(data["timestamp"].iloc[-1])
    # elif source == "binance": old = datetime.strptime('1 Jan 2017', '%d %b %Y')
    new = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=True).result()[0][0]['timestamp']
    old = new - timedelta(minutes=120)
    # if source == "binance": new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')
    # if source == "bitmex": new = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=True).result()[0][0]['timestamp']
    return old, new


def get_all_bitmex(symbol, kline_size, save = False):
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename): data_df = pd.read_csv(filename)
    else: data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source = "bitmex")
    # oldest_point = datetime(2020, 4, 22, tzinfo=tzutc())
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    rounds = math.ceil(available_data / batch_size)
    # rounds = 100
    print("rounds ")
    print(range(rounds))
    print(type(oldest_point))
    print(newest_point)
    # print(tqdm_notebook(range(rounds)))
    # exit()
    if rounds > 0:
        print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data in %d rounds.' % (delta_min, symbol, available_data, kline_size, rounds))
        for round_num in range(rounds):
            # print('-')
            # print(round_num)
        # for round_num in tqdm_notebook(range(rounds)):
            time.sleep(1)
            new_time = (oldest_point + timedelta(minutes = round_num * batch_size * binsizes[kline_size]))
            data = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=batch_size, startTime = new_time).result()[0]

            temp_df = pd.DataFrame(data)
            data_df = data_df.append(temp_df)
    # data_df.set_index('timestamp', inplace=True)
    if save and rounds > 0: data_df.to_csv(filename)
    # get_mean_open_close(data_df)
    print('Data_df tendance')
    print(data_df.close.mean() - data_df.open.mean())
    print('All caught up..!')
    if data_df.open.mean() - data_df.close.mean() < 0:
        print("baissiere")
    else:
        print('haussiere')
    return data_df