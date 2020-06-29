# IMPORTS
import pandas as pd
import math
import os.path
import time
from bitmex import bitmex
import matplotlib.pyplot as plt
import numpy as np
import tulipy as ti

# from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
from dateutil.tz import tzutc
from finta import TA
from jsonref import requests
from tqdm import tqdm_notebook #(Optional, used for progress-bars)
from market_maker.settings import settings

### API
from market_maker.utils.dotdict import dotdict

# set = {}
# set = dotdict(settings)
### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440, "15m": 15}
batch_size = 750
bitmex_client = bitmex(test=True, api_key=settings.API_KEY, api_secret=settings.API_SECRET)
# binance_client = Client(api_key=binance_api_key, api_secret=binance_api_secret)


### FUNCTIONS
def minutes_of_new_data(symbol, kline_size, data, source, nb):
    if len(data) > 0:  old = parser.parse(data["timestamp"].iloc[-1])
    # elif source == "binance": old = datetime.strptime('1 Jan 2017', '%d %b %Y')
    new = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=True).result()[0][0]['timestamp']
    old = new - timedelta(minutes=nb)
    # if source == "binance": new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')
    # if source == "bitmex": new = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=True).result()[0][0]['timestamp']
    return old, new


def get_all_bitmex(symbol, kline_size, save=False, rounds=None, nb=120):
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename): data_df = pd.read_csv(filename)
    else: data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source="bitmex", nb=nb)
    # oldest_point = datetime(2020, 4, 22, tzinfo=tzutc())
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    rounds = math.ceil(available_data / batch_size)
    if rounds > 0:
        print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data in %d rounds.' % (delta_min, symbol, available_data, kline_size, rounds))
        for round_num in range(rounds):
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


def get_prices_binsize(prices, binsize):
    new_prices = []
    # i = 1
    # while i < len(prices):
    #     new_prices.append(prices[i])
    #     i += binsize
    for x in range(1, len(prices), binsize):
        new_prices.append(prices[x])
    return new_prices

def get_mean_open_close(number=120, kline_size='1m'):
    prices = []

    # A utiliser que pour testnet !!
    # link = str(settings.BASE_URL) + "trade?symbol=XBTUSD&count="\
    #        + str(number * binsizes[kline_size]) + "&columns=price&reverse=true"


    link_ohlc = "https://www.bitmex.com/api/v1/trade/bucketed?binSize=1m&partial=true&symbol=XBTUSD&count=20&reverse=true"
    f = requests.get(link_ohlc)
    ohlc = pd.DataFrame(f.json())
    ohlc = ohlc[['open', 'high', 'low', 'close']]
    # datta = TA.bb


    link = str(settings.BASE_URL) + "trade?symbol=.BXBT&count="\
           + str(number * binsizes[kline_size]) + "&columns=price&reverse=true"
    f = requests.get(link)
    for x in f.json():
        prices.append(float(x['price']))
    prices = get_prices_binsize(prices, binsizes[kline_size])
    prices.reverse()


    # Library Tulipy
    DATA = np.array(prices)
    bbands = ti.bbands(DATA, period=5, stddev=2)

    res = TA.BBANDS(get_all_bitmex('XBTUSD', kline_size, False, nb=(number * 2 * binsizes[kline_size])))
    temp_df = pd.DataFrame()
    temp_df['BB_LOWER'] = bbands[0][-1:]
    temp_df['BB_MIDDLE'] = bbands[1][-1:]
    temp_df['BB_UPPER'] = bbands[2][-1:]
    #
    #   AFFICHAGE COURBES
    #

    low = list(bbands[0])
    middle = list(bbands[1])
    high = list(bbands[2])

    low = list(res.BB_LOWER[-number:])
    middle = list(res.BB_MIDDLE[-number:])
    high = list(res.BB_UPPER[-number:])

    # plt.plot(high, color='orange')
    # plt.plot(middle, color='g')
    # plt.plot(low, color='yellow')
    # plt.plot(prices, color='red')
    # plt.show()


    # return temp_df
    return res[-number:], bbands
