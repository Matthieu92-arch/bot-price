from ast import literal_eval

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

def adjust_bbs(current, last_price, bbands, funding):
    if current.BB_UPPER.item() < last_price:
        current.BB_UPPER = last_price + 1
    elif current.BB_LOWER.item() > last_price:
        current.BB_LOWER = last_price - 1
    if current.BB_MIDDLE.item() < last_price:
        current.BB_MIDDLE = last_price
    elif current.BB_MIDDLE.item() > last_price:
        current.BB_MIDDLE = last_price

    if last_price - current.BB_LOWER.item() > 40 and funding < 0:
        current.BB_LOWER = last_price - 20
    elif last_price - current.BB_LOWER.item() > 90:
        current.BB_LOWER = last_price - 40
    if current.BB_UPPER.item() - last_price > 40 and funding > 0:
        current.BB_UPPER = last_price + 20
    if current.BB_UPPER.item() - last_price > 90:
        current.BB_UPPER = last_price + 40
    return current


def get_phase_normal(bb, bbands, last_price, entry_price, quantity, funding):
    prices_up = []
    prices_down = []
    current = bb[-1:]
    spread_pctg = 0.15

    current = adjust_bbs(current, last_price, bbands, funding)

    spread_up = (round(current.BB_UPPER) - round(current.BB_MIDDLE)) / 4
    spread_bottom = (round(current.BB_MIDDLE) - round(current.BB_LOWER)) / 4
    spread_up = 3 if spread_up.item() <= 3 else spread_up
    spread_bottom = 3 if spread_bottom.item() <= 3 else spread_bottom

    middle_up = current.BB_MIDDLE
    if entry_price and entry_price > current.BB_MIDDLE.item() and quantity > 0:
        middle_up = entry_price
    for i in range(0, 5):
        prices_up.append(round(middle_up) + (spread_up * (i + 1)))
    if entry_price and current.BB_UPPER.item() < entry_price:
        current.BB_UPPER = entry_price
    prices_up.append(round(current.BB_UPPER) * (100 + spread_pctg) / 100)
    prices_up.append(round(current.BB_UPPER) * (100 + spread_pctg * 2) / 100)
    prices_up.append(round(current.BB_UPPER) * (100 + spread_pctg * 4) / 100)
    prices_up.append(round(current.BB_UPPER) * (100 + 1) / 100)

    middle_down = current.BB_MIDDLE
    if entry_price and entry_price < current.BB_MIDDLE.item() and quantity < 0:
        middle_down = entry_price
    for i in range(0, 5):
        prices_down.append(round(middle_down) - (spread_bottom * (i + 1)))
    if entry_price and current.BB_LOWER.item() > entry_price:
        current.BB_LOWER = entry_price
    prices_down.append(round(current.BB_LOWER) * (100 - spread_pctg) / 100)
    prices_down.append(round(current.BB_LOWER) * (100 - spread_pctg * 2) / 100)
    prices_down.append(round(current.BB_LOWER) * (100 - spread_pctg * 4) / 100)
    prices_down.append(round(current.BB_LOWER) * (100 - 1) / 100)


    return prices_up, prices_down


def get_phase_middle(bb, bbands, quantity, last_price, entry_price, funding):
    prices_up = []
    prices_down = []
    current = bb[-1:]
    spread_pctg = 0.15

    current = adjust_bbs(current, last_price, bbands, funding)

    middle_up = current.BB_MIDDLE.item() + 0.5
    middle_down = current.BB_MIDDLE.item() - 0.5
    if quantity > 0:
        middle_down = current.BB_LOWER - 10
        middle_up = round(entry_price) + 0.5
        if middle_up < last_price:
            middle_up = last_price + 0.5
    if quantity < 0:
        middle_up = current.BB_UPPER + 10
        middle_down = round(entry_price) - 0.5
        if middle_down > last_price:
            middle_down = last_price - 0.5

    if quantity > 0:
        spread_up = (round(current.BB_UPPER) - round(current.BB_MIDDLE)) / 6
        spread_up = 3 if spread_up.item() <= 3 else spread_up

        for i in range(1, 8):
            prices_up.append(round(middle_up) + (spread_up * (i - 1)))
        if current.BB_UPPER.item() < entry_price:
            prices_up.append(round(middle_up) * (100 + 0.5) / 100)
            prices_up.append(round(middle_up) * (100 + 1.5) / 100)
        else:
            prices_up.append(round(current.BB_UPPER) * (100 + 0.5) / 100)
            prices_up.append(round(current.BB_UPPER) * (100 + 1.5) / 100)
        for i in range(0, 8):
            prices_down.append(round(current.BB_LOWER) * (100 - ((i + 1) * spread_pctg)) / 100)
        prices_down.append(round(current.BB_LOWER) * (100 - 1.5) / 100)

    if quantity < 0:
        spread_bottom = (round(current.BB_MIDDLE) - round(current.BB_LOWER)) / 6
        spread_bottom = 3 if spread_bottom.item() <= 3 else spread_bottom

        for i in range(1, 8):
            prices_down.append(round(middle_down) - (spread_bottom * (i - 1)))
        if current.BB_LOWER.item() > entry_price:
            prices_down.append(round(middle_down) * (100 - 0.5) / 100)
            prices_down.append(round(middle_down) * (100 - 1.5) / 100)
        else:
            prices_down.append(round(current.BB_LOWER) * (100 - 0.5) / 100)
            prices_down.append(round(current.BB_LOWER) * (100 - 1.5) / 100)
        for i in range(0, 8):
            prices_up.append(round(current.BB_UPPER) * (100 + ((i + 1) * spread_pctg)) / 100)
        prices_up.append(round(current.BB_UPPER) * (100 + 1.5) / 100)

    return prices_up, prices_down


def get_phase_low(bb, bbands, quantity, last_price, funding):
    prices_up = []
    prices_down = []
    current = bb[-1:]
    spread_pctg = 0.30

    current = adjust_bbs(current, last_price, bbands, funding)

    if quantity > 0:
        spread_up = (round(current.BB_UPPER) - round(current.BB_MIDDLE)) / 7
        spread_up = 3 if spread_up.item() <= 3 else spread_up

        for i in range(0, 9):
            prices_up.append(round(current.BB_MIDDLE) + (spread_up * i))
        prices_up.append(round(current.BB_UPPER) * (100 + 2.5) / 100)
        for i in range(0, 9):
            prices_down.append(round(current.BB_LOWER) * (100 - (i * spread_pctg)) / 100)
        prices_down.append(round(current.BB_LOWER) * (100 - 2.5) / 100)


    if quantity < 0:
        spread_bottom = (round(current.BB_MIDDLE) - round(current.BB_LOWER)) / 7
        spread_bottom = 3 if spread_bottom.item() <= 3 else spread_bottom
        for i in range(0, 9):
            prices_down.append(round(current.BB_MIDDLE) - (spread_bottom * i))
        prices_down.append(round(current.BB_LOWER) * (100 - 2.5) / 100)
        for i in range(0, 9):
            prices_up.append(round(current.BB_UPPER) * (100 + (i * spread_pctg)) / 100)
        prices_up.append(round(current.BB_UPPER) * (100 + 2.5) / 100)


    return prices_up, prices_down


def get_price(wallet, bb, bbands, quantity, last_price, entry_price, funding):
    prices_up = []
    prices_down = []
    if wallet >= 75:
        prices_up, prices_down = get_phase_normal(bb, bbands, last_price, entry_price, quantity, funding)
    elif wallet >= 60:
        prices_up, prices_down = get_phase_middle(bb, bbands, quantity, last_price, entry_price, funding)
    elif wallet >= 45:
        prices_up, prices_down = get_phase_low(bb, bbands, quantity, last_price, funding)
    ##
    ##              FINISH
    ##
    else:
        prices_up, prices_down = get_phase_low(bb, bbands, quantity, last_price, funding)

    return prices_up, prices_down


def clean_prices(prices_up, prices_down):
    ret_up, ret_down = [], []
    i = 1
    for x in prices_up:
        if isinstance(x, int) or isinstance(x, float):
            ret_up.append(round(x) + (0.5 * i))
        elif x.item() in ret_up:
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


# def reajust_qty(position, quantity, side, index, wallet):
#     if (position > 300 and side == "Sell") or (position < -300 and side == "Buy"):
#         quantity += settings.ORDER_BALANCE_STEP_SIZE
#     if (position > 500 and side == "Sell") or (position < -500 and side == "Buy"):
#         quantity = round((position * - 1) / 5)
#
#     return quantity


def get_quantity(position, side, index, wallet, quantity, funding):
    if wallet > 93:
        return quantity
    elif wallet >= 75 and (position > -200 or position < 200):
        if position < 0 and side == 'Buy':
            if funding < 0:
                return round(quantity * 1.16)
            return quantity
        elif position > 0 and side == 'Sell':
            if funding > 0:
                return round(quantity * 1.16)
            return quantity
        return quantity
    elif wallet >= 75:
        if position < 0 and side == 'Buy':
            if funding < 0:
                return round(quantity * 1.46)
            return round(quantity * 1.25)
        elif position > 0 and side == 'Sell':
            if funding > 0:
                return round(quantity * 1.46)
            return round(quantity * 1.25)
        return quantity
    elif wallet >= 60:
        if position < 0 and side == 'Buy':
            if funding < 0:
                return round(quantity * 1.53)
            return round(quantity * 1.4)
        elif position > 0 and side == 'Sell':
            if funding > 0:
                return round(quantity * 1.53)
            return round(quantity * 1.4)
        return quantity
    else:
        if position < 0 and side == 'Buy':
            if funding < 0:
                return round(quantity * 2.25)
            return round(quantity * 2)
        elif position > 0 and side == 'Sell':
            if funding > 0:
                return round(quantity * 2.25)
            return round(quantity * 2)
        return quantity
    # else:
    #     if position < 0 and side == 'Buy':
    #         if funding < 0:
    #             return round(quantity * 3.5)
    #         return quantity * 3
    #     elif position > 0 and side == 'Sell':
    #         if funding > 0:
    #             return round(quantity * 3.5)
    #         return quantity * 3
    #     return quantity
    return quantity



def tri_orders(position, existing_orders, buy_orders, sell_orders):
    buys_matched = 0
    sells_matched = 0
    for order in existing_orders:
        if order['side'] == 'Buy':
            buys_matched += 1
        else:
            sells_matched += 1

    if position['currentQty'] > 0:
        if buys_matched < 4:
            return buy_orders, sell_orders
        elif existing_orders:
            existing_orders = [k for k in existing_orders if k['side'] == 'Sell']
    if position['currentQty'] < 0:
        if sells_matched < 4:
            return buy_orders, sell_orders
        elif existing_orders:
            existing_orders = [k for k in existing_orders if k['side'] == 'Buy']
    return buy_orders, sell_orders
