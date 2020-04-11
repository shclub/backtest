from collections import namedtuple

import numpy as np

Tick = namedtuple('Tick',
                  'symbol price volume timestamp')
Order = namedtuple('Order',
                   'symbol price quantity timestamp')
Filled = namedtuple('Filled',
                    'timestamp symbol quantity price commission tax slippage')


class Stock:
    def __init__(self, size=100, keep=30):
        self._size = size
        self._keep = keep
        self._watermark = -1
        self._timestamp = -1

        self.stoploss = None
        self.columns = {'price': np.zeros(size, dtype=float),
                        'volume': np.zeros(size, dtype=float)}

    def __len__(self):
        return self._size

    def __getitem__(self, item):
        return self.columns[item]

    def __iadd__(self, tick):
        if self._timestamp == tick.timestamp:
            self._update(tick)
        else:
            self._add(tick)

        return self

    def _update(self, tick):
        i = self._watermark
        self['price'][i] = tick.price
        self['volume'][i] += tick.volume

    def _add(self, tick):
        if len(self) == self._watermark + 1:
            self._erase_old()
            self._watermark = self._keep - 1

        i = self._watermark + 1
        self['price'][i] = tick.price
        self['volume'][i] = tick.volume
        self._timestamp = tick.timestamp
        self._watermark = i

    def _erase_old(self):
        for name in self.columns.keys():
            arr = self.columns[name]
            arr[:self._keep] = arr[-self._keep:]  # bring forward the given number of back items
            arr[self._keep:] = 0  # then make zero the remaining

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'columns={[col for col in self.columns]}, '
                f'length={len(self)}, '
                f'watermark={self._watermark}, '
                f'stoploss={self.stoploss}'
                f')')
