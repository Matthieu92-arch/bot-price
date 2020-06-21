from jsonref import requests
from pandas import np
from finta import TA
import matplotlib.pyplot as plt

import settings
from get_bitmex import get_all_bitmex


# def get_mean_open_close(number=120, kline_size='1m'):
#     prices = []
#     link = "https://www.bitmex.com/api/v1/trade?symbol=.BXBT&count=120&columns=price&reverse=true"
#
#     f = requests.get(link)
#     for x in f.json():
#         prices.append(x['price'])
#     prices.reverse()
#
#     # DATA = np.array(prices)
#     # bbands = ti.bbands(DATA, period=5, stddev=2)
#
#     res = TA.BBANDS(get_all_bitmex('XBTUSD', kline_size, False, nb=number))
#
#     low = list(res.BB_LOWER[120:])
#     middle = list(res.BB_MIDDLE[120:])
#     high = list(res.BB_UPPER[120:])
#
#     plt.plot(high, color='orange')
#     plt.plot(middle, color='g')
#     plt.plot(low, color='yellow')
#     plt.plot(prices, color='red')
#     plt.show()
#
#     # price = data_df.copy()
#     # price['price'] = price.open
#     return res

def adjust_bbs(current, last_price):
    if current.BB_UPPER.item() < last_price:
        current.BB_UPPER = last_price + 1
    elif current.BB_LOWER.item() > last_price:
        current.BB_LOWER = last_price - 1
    if current.BB_MIDDLE.item() < last_price:
        current.BB_MIDDLE = last_price
    elif current.BB_MIDDLE.item() > last_price:
        current.BB_MIDDLE = last_price

    return current


def get_phase_normal(bb, last_price, entry_price):
    prices_up = []
    prices_down = []
    current = bb[-1:]
    spread_pctg = 0.15

    current = adjust_bbs(current, last_price)

    spread_up = (round(current.BB_UPPER) - round(current.BB_MIDDLE)) / 4
    spread_bottom = (round(current.BB_MIDDLE) - round(current.BB_LOWER)) / 4
    spread_up = 3 if spread_up.item() <= 3 else spread_up
    spread_bottom = 3 if spread_bottom.item() <= 3 else spread_bottom

    middle_up = current.BB_MIDDLE
    if entry_price > current.BB_MIDDLE.item():
        middle_up = entry_price
    for i in range(0, 5):
        prices_up.append(round(middle_up) + (spread_up * (i + 1)))
    if current.BB_UPPER.item() < entry_price:
        current.BB_UPPER = entry_price
    prices_up.append(round(current.BB_UPPER) * (100 + spread_pctg) / 100)
    prices_up.append(round(current.BB_UPPER) * (100 + spread_pctg * 2) / 100)
    prices_up.append(round(current.BB_UPPER) * (100 + spread_pctg * 4) / 100)

    middle_down = current.BB_MIDDLE
    if entry_price < current.BB_MIDDLE.item():
        middle_down = entry_price
    for i in range(0, 5):
        prices_down.append(round(middle_down) - (spread_bottom * (i + 1)))
    if current.BB_LOWER.item() > entry_price:
        current.BB_LOWER = entry_price
    prices_down.append(round(current.BB_LOWER) * (100 - spread_pctg) / 100)
    prices_down.append(round(current.BB_LOWER) * (100 - spread_pctg * 2) / 100)
    prices_down.append(round(current.BB_LOWER) * (100 - spread_pctg * 4) / 100)


    return prices_up, prices_down


def get_phase_middle(bb, quantity, last_price, entry_price):
    prices_up = []
    prices_down = []
    current = bb[-1:]
    spread_pctg = 0.15

    current = adjust_bbs(current, last_price)

    # if current.BB_MIDDLE.item() < last_price:
    #     current.BB_MIDDLE = last_price
    middle_up = current.BB_MIDDLE
    if entry_price > current.BB_MIDDLE.item():
        middle_up = entry_price
    middle_down = current.BB_MIDDLE
    if entry_price < current.BB_MIDDLE.item():
        middle_down = entry_price


    if quantity > 0:
        spread_up = (round(current.BB_UPPER) - round(current.BB_MIDDLE)) / 6
        spread_up = 3 if spread_up.item() <= 3 else spread_up

        for i in range(1, 8):
            prices_up.append(round(middle_up) + (spread_up * i))
        if current.BB_UPPER.item() < entry_price:
            prices_up.append(round(middle_up) * (100 + spread_pctg) / 100)
        else:
            prices_up.append(round(current.BB_UPPER) * (100 + spread_pctg) / 100)
        for i in range(0, 8):
            prices_down.append(round(current.BB_LOWER) * (100 - (i * spread_pctg)) / 100)

    if quantity < 0:
        spread_bottom = (round(current.BB_MIDDLE) - round(current.BB_LOWER)) / 6
        spread_bottom = 3 if spread_bottom.item() <= 3 else spread_bottom
        for i in range(1, 8):
            prices_down.append(round(middle_down) - (spread_bottom * i))
        if current.BB_LOWER.item() > entry_price:
            prices_down.append(round(middle_down) * (100 - spread_pctg) / 100)
        else:
            prices_down.append(round(current.BB_LOWER) * (100 - spread_pctg) / 100)
        for i in range(0, 8):
            prices_up.append(round(current.BB_UPPER) * (100 + (i * spread_pctg)) / 100)

    return prices_up, prices_down


def get_phase_low(bb, quantity, last_price):
    prices_up = []
    prices_down = []
    current = bb[-1:]
    spread_pctg = 0.30

    current = adjust_bbs(current, last_price)

    # if current.BB_MIDDLE.item() < last_price:
    #     current.BB_MIDDLE = last_price

    if quantity > 0:
        spread_up = (round(current.BB_UPPER) - round(current.BB_MIDDLE)) / 7
        spread_up = 3 if spread_up.item() <= 3 else spread_up

        for i in range(0, 8):
            prices_up.append(round(current.BB_MIDDLE) + (spread_up * i))
        for i in range(0, 8):
            prices_down.append(round(current.BB_LOWER) * (100 - (i * spread_pctg)) / 100)

    if quantity < 0:
        spread_bottom = (round(current.BB_MIDDLE) - round(current.BB_LOWER)) / 7
        spread_bottom = 3 if spread_bottom.item() <= 3 else spread_bottom
        for i in range(0, 8):
            prices_down.append(round(current.BB_MIDDLE) - (spread_bottom * i))
        for i in range(0, 8):
            prices_up.append(round(current.BB_UPPER) * (100 + (i * spread_pctg)) / 100)

    return prices_up, prices_down


def get_price(wallet, bb, quantity, last_price, entry_price):
    prices_up = []
    prices_down = []
    if wallet >= 75:
        prices_up, prices_down = get_phase_normal(bb, last_price, entry_price)
    elif wallet >= 60:
        prices_up, prices_down = get_phase_middle(bb, quantity, last_price, entry_price)
    elif wallet >= 45:
        prices_up, prices_down = get_phase_low(bb, quantity, last_price)
    ##
    ##              FINISH
    ##
    else:
        prices_up, prices_down = get_phase_low(bb, quantity, last_price)

    return prices_up, prices_down


def clean_prices(prices_up, prices_down):
    ret_up, ret_down = [], []
    i = 1
    for x in prices_up:
        if isinstance(x, int):
            ret_down.append(round(x) + (0.5 * i))
        if x.item() in ret_up:
            ret_up.append(round(x.item()) + (0.5 * i))
        else:
            ret_up.append(round(x.item()))
        i += 1

    i = 1
    for x in prices_down:
        if isinstance(x, int) or isinstance(x, float):
            ret_down.append(round(x) - (0.5 * i))
        elif x.item() in ret_up:
            ret_down.append(round(x.item()) - (0.5 * i))
        else:
            ret_down.append(round(x.item()))
        i += 1

    return ret_up, ret_down

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
        index = (index * -1)
    if not entry_price:
        return round(desired_price)

    ### Rapprocher ordres de entry_price si position commence à grandir
    if side == 'Buy' and desired_price > entry_price and quantity < -700:
        return round(((entry_price * 2) / 2) - 0.5 - (index))
    elif side == 'Sell' and desired_price < entry_price and quantity > 700:
        return round(((entry_price * 2) / 2) + 0.5 + (index))


    ### Rapprocher prix de l'entry price si possible de close position de suite
    ### Baisse de gains mais safe
    if side == 'Buy' and desired_price < entry_price and quantity < -350:
        return round(((entry_price * 2) / 2) - 0.5 - (index * 1))
    elif side == 'Sell' and desired_price > entry_price and quantity > 350:
        return round(((entry_price * 2) / 2) + 0.5 + (index * 1))


    ### Ecarter prix CONTRE POSITION
    if quantity < -750 and side == "Buy":
        return round(((entry_price * 2) / 2) - 0.5 - (index))
    elif quantity > 750 and side == "Sell":
        return round(((entry_price * 2) / 2) + 0.5 + (index))

    if quantity < -2500 and side == "Sell":
        return round(desired_price + 5 + (index))
    elif quantity > 2500 and side == "Buy":
        return round(desired_price - 5 -(index))


    if quantity < -2000 and side == "Sell":
        return round(desired_price + 5 + (index))
    elif quantity > 2000 and side == "Buy":
        return round(desired_price - 5 -(index))

    if quantity < -750 and side == "Sell":
        return round(desired_price + (index))
    elif quantity > 750 and side == "Buy":
        return round(desired_price - (index))


    if side == 'Buy' and desired_price > entry_price:
        return round(entry_price - (index * 0.5))
    elif side == 'Sell' and desired_price < entry_price:
        return round(entry_price + (index * 0.5))

    return round(desired_price)