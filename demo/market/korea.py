import json
from pathlib import Path

import numpy as np

FILES = {'symbols':
             {'kospi': 'symbols_kospi.json',
              'kosdaq': 'symbols_kosdaq.json'},
         'rules':
             {'kospi': 'rules_kospi.json',
              'kosdaq': 'rules_kosdaq.json'}}

symbols = {}
for market, path in FILES['symbols'].items():
    with Path(__file__).parent.joinpath(path).open(encoding='utf-8') as f:
        symbols[market] = json.load(f).keys()

rules = {}
for market, path in FILES['rules'].items():
    with Path(__file__).parent.joinpath(path).open(encoding='utf-8') as f:
        rules[market] = json.load(f)


def get_market(symbol: str) -> str:
    return 'kospi' if symbol in symbols['kospi'] else 'kosdaq'


def simulate_price(market, price, quantity) -> float:
    mean = 0.5 if quantity > 0 else -0.5,
    slippage_stdev = 0.7
    offset = int(np.random.normal(mean, slippage_stdev))

    unit = get_unit(market, price)

    return price + offset * unit


def get_unit(market, price) -> float:
    items = rules[market]['price_units']
    for item in items:
        if price < item['price']:
            return item['unit']

    return items[-1]['unit']


def calc_commission(market, price, quantity) -> float:
    trade = 'buy' if quantity > 0 else 'sell'
    rate = rules[market]['commission'][trade]

    return round(price * abs(quantity) * rate)


def calc_tax(market, price, quantity) -> float:
    trade = 'buy' if quantity > 0 else 'sell'
    rate = rules[market]['tax'][trade]

    return round(price * abs(quantity) * rate)