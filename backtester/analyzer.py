import json
import queue
import time
import logging
import logging.config

from collections import defaultdict
from logging.handlers import QueueHandler
from multiprocessing import Event

from .data import Dataset, Order

logger = logging.getLogger('analyzer')


def _init_logger(log_queue):
    logging_config = json.load(open('config/logging.json'))
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger('analyzer')
    logger.addHandler(QueueHandler(log_queue))


def run(config, strategy, cash, quantity_dict, tick_queue, order_queue, log_queue, done: Event):
    _init_logger(log_queue)

    dataset_dict = defaultdict(Dataset)
    stoploss_dict = defaultdict(float)

    count = 0
    while not done.is_set():
        try:
            t = tick_queue.get(block=True, timeout=0.1)
        except queue.Empty:
            continue

        holding = quantity_dict.get(t.symbol, 0)
        stoploss = stoploss_dict[t.symbol]
        dataset = dataset_dict[t.symbol]
        dataset += t

        if holding > 0 and t.price < stoploss:
            quantity = strategy.calc_quantity_to_sell(holding, dataset)
        else:
            quantity = strategy.calc_quantity_to_buy(config['initial_cash'], cash.value, holding, dataset)

        if abs(quantity) > 0:
            order = Order(t.symbol, t.price, quantity, t.timestamp)
            order_queue.put(order)

        if quantity > 0 or holding > 0:
            stoploss_dict[t.symbol] = strategy.calc_stoploss(stoploss, dataset)

        count += 1

    logger.info(f'Analyzed {count} ticks')
