# coding:utf-8

from time import time
from typing import Any
from typing import Dict
from typing import Generic
from typing import Optional
from typing import TypeVar
from typing import Union

from .thread import NamedLock

INT = TypeVar("INT")
IDT = TypeVar("IDT")
PIT = TypeVar("PIT")
PVT = TypeVar("PVT")

CacheTimeout = Union[float, int]


class CacheLookup(LookupError):
    pass


class CacheMiss(CacheLookup):
    def __init__(self, name: Any):
        super().__init__(f"Not found {name} in cache")


class CacheExpired(CacheLookup):
    def __init__(self, name: Any):
        super().__init__(f"Cache {name} expired")


class CacheItem(Generic[INT, IDT]):
    def __init__(self, name: INT, data: IDT, lifetime: CacheTimeout = 0):
        self.__lifetime: float = float(lifetime)
        self.__timestamp: float = time()
        self.__name: INT = name
        self.__data: IDT = data

    @property
    def up(self) -> float:
        return self.__timestamp

    @property
    def age(self) -> float:
        return time() - self.up

    @property
    def life(self) -> float:
        return self.__lifetime

    @property
    def expired(self) -> bool:
        return self.life > 0.0 and self.age > self.life

    @property
    def name(self) -> INT:
        return self.__name

    @property
    def data(self) -> IDT:
        if self.expired:
            raise CacheExpired(self.name)
        return self.__data


class CachePool(Generic[PIT, PVT]):

    def __init__(self, lifetime: CacheTimeout = 0):
        self.__pool: Dict[PIT, CacheItem[PIT, PVT]] = {}
        self.__namedlock: NamedLock[PIT] = NamedLock()
        self.__lifetime: float = float(lifetime)

    def __setattr__(self, index: PIT, value: PVT) -> None:
        return self.put(index, value)

    def __getitem__(self, index: PIT) -> PVT:
        return self.get(index)

    def __delitem__(self, index: PIT) -> None:
        return self.delete(index)

    @property
    def lifetime(self) -> float:
        return self.__lifetime

    def put(self, index: PIT, value: PVT, lifetime: Optional[CacheTimeout] = None) -> None:  # noqa:E501
        life = lifetime if lifetime is not None else self.lifetime
        item = CacheItem(index, value, life)
        with self.__namedlock[index]:
            self.__pool[index] = item

    def get(self, index: PIT) -> PVT:
        with self.__namedlock[index]:
            try:
                item = self.__pool[index]
                data = item.data
                return data
            except CacheExpired as exc:
                del self.__pool[index]
                assert index not in self.__pool
                raise CacheMiss(index) from exc
            except KeyError as exc:
                raise CacheMiss(index) from exc

    def delete(self, index: PIT) -> None:
        with self.__namedlock[index]:
            if index in self.__pool:
                del self.__pool[index]
