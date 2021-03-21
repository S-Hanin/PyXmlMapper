from .common import Default
from collections.abc import Iterable, Sized


class Selector(Iterable, Sized):
    def __init__(self, items, default=""):
        self._default = default
        self._items = items

    def first(self):
        if not len(self._items):
            return Default(self._default)
        return self._items[0]

    def last(self):
        if not len(self._items):
            return Default(self._default)
        return self._items[-1]

    def item(self, index):
        if len(self._items) < abs(index):
            return Default(self._default)
        return self._items[index]

    def all(self):
        return self._items

    def __len__(self):
        return len(self._items)

    def __getitem__(self, item):
        return self._items[item]

    def __iter__(self):
        for item in self._items:
            yield item
