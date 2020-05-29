import os
import sys

from jsonref import requests
from pandas import np
from finta import TA

import settings
import tulipy as ti
import matplotlib.pyplot as plt
import market_maker._settings_base as baseSettings

from market_maker import bitmex
from market_maker.market_maker import OrderManager
from market_maker.settings import import_path
from market_maker.utils import log
from market_maker.utils.dotdict import dotdict

logger = log.setup_custom_logger('root')


class CustomOrderManager(OrderManager):
    """A sample order manager for implementing your own custom strategy"""
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        if len(sys.argv) > 1:
            self.symbol = sys.argv[1]
        else:
            self.symbol = settings.SYMBOL
        self.bitmex = bitmex.BitMEX(base_url=settings.BASE_URL, symbol=self.symbol,
                                    apiKey=settings.API_KEY, apiSecret=settings.API_SECRET,
                                    orderIDPrefix=settings.ORDERID_PREFIX, postOnly=settings.POST_ONLY,
                                    timeout=settings.TIMEOUT)

    def place_orders(self) -> None:
        # implement your custom strategy here

        buy_orders = []
        sell_orders = []

        # populate buy and sell orders, e.g.
        # buy_orders.append({'price': 999.0, 'orderQty': 100, 'side': "Buy"})
        # sell_orders.append({'price': 1001.0, 'orderQty': 100, 'side': "Sell"})
        self.converge_orders(buy_orders, sell_orders)


    def run(self) -> None:
        link = "https://www.bitmex.com/api/v1/trade?symbol=.BXBT&count=200&columns=price&reverse=true"
        f = requests.get(link)
        prices = []
        for x in f.json():
            prices.append(x['price'])

        print(prices)
        prices.reverse()
        DATA = np.array(prices)
        bbands = ti.bbands(DATA, period=5, stddev=2)
        high = bbands[0]
        middle = bbands[1]
        low = bbands[2]
        # plt.plot(high, color='orange')
        # plt.plot(prices, color='g')
        # plt.plot(low, color='yellow')
        # plt.show()

        order_manager = OrderManager()

        # Try/except just keeps ctrl-c from printing an ugly stacktrace
        try:
            self.bitmex.ws.recent_trades()
            order_manager.run_loop()
        except (KeyboardInterrupt, SystemExit):
            sys.exit()


userSettings = import_path(os.path.join('.', 'settings'))
symbolSettings = None
symbol = sys.argv[1] if len(sys.argv) > 1 else None
if symbol:
    print("Importing symbol settings for %s..." % symbol)
    try:
        symbolSettings = import_path(os.path.join('..', 'settings-%s' % symbol))
    except Exception as e:
        print("Unable to find settings-%s.py." % symbol)

settings = {}
settings.update(vars(baseSettings))
settings.update(vars(userSettings))
if symbolSettings:
    settings.update(vars(symbolSettings))

# Main export
settings = dotdict(settings)

e = CustomOrderManager()
e.run()

