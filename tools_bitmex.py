from jsonref import requests
from pandas import np
from finta import TA
import matplotlib.pyplot as plt

import settings


def get_mean_open_close(data_df):
    link = "https://www.bitmex.com/api/v1/trade?symbol=.BXBT&count=120&columns=price&reverse=true"
    f = requests.get(link)
    prices = []
    for x in f.json():
        prices.append(x['price'])

    print(prices)
    prices.reverse()
    DATA = np.array(prices)
    res = TA.BBANDS(data_df)
    low = list(res.BB_LOWER)
    middle = list(res.BB_MIDDLE)
    high = list(res.BB_UPPER)

    # plt.plot(high, color='orange')
    # plt.plot(middle, color='g')
    # plt.plot(low, color='yellow')
    # plt.plot(prices, color='red')
    # plt.show()

    price = data_df.copy()
    price['price'] = price.open
    return price


##          VERSION 1
## -----------------------------

# def reajust_qty(position, quantity, side):
#     if (position > 300 and side == "Sell") or (position < -300 and side == "Buy"):
#         quantity += 25
#     if (position > 500 and side == "Sell") or (position < -500 and side == "Buy"):
#         quantity += 40
#     if (position > 700 and side == "Sell") or (position < -700 and side == "Buy"):
#         quantity += 60
#     if (position > 1000 and side == "Sell") or (position < -1000 and side == "Buy"):
#         quantity += 80
#
#     return quantity


##          VERSION 2
## -----------------------------
# def reajust_qty(position, quantity, side, index):
#     if (position > 300 and side == "Sell") or (position < -300 and side == "Buy"):
#         quantity += 35
#     if (position > 500 and side == "Sell") or (position < -500 and side == "Buy"):
#         quantity += 50
#     if (position > 700 and side == "Sell") or (position < -700 and side == "Buy"):
#         quantity += 75
#     if (position > 1000 and side == "Sell") or (position < -1000 and side == "Buy"):
#         quantity = round((position * - 1) / 5)
#
#     return quantity


def reajust_qty(position, quantity, side, index):
    if (position > 300 and side == "Sell") or (position < -300 and side == "Buy"):
        quantity += settings.ORDER_BALANCE_STEP_SIZE
    if (position > 500 and side == "Sell") or (position < -500 and side == "Buy"):
        quantity = round((position * - 1) / 5)

    return quantity


def reajust_price(entry_price, desired_price, side, quantity, index):
    if index < 0:
        index = index + (index * 2 * -1)
    if not entry_price:
        return desired_price
    if desired_price > entry_price and quantity < 0:
        if side == 'Buy':
            return (round(entry_price * 2) / 2) - 0.5 - (index * -0.5)
        else:
            return (round(entry_price * 2) / 2) + 0.5 + (index * -1)
    elif desired_price < entry_price and quantity > 0:
        if side == 'Sell':
            return (round(entry_price * 2) / 2) + 0.5 + (index * 0.5)
        else:
            return (round(entry_price * 2) / 2) + 0.5 + index
    return desired_price