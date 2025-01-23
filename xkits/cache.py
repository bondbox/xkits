# coding:utf-8

from threading import Lock
from time import time
from typing import Any
from typing import Dict
from typing import Generator
from typing import Generic
from typing import Optional
from typing import TypeVar
from typing import Union

ANT = TypeVar("ANT")
ADT = TypeVar("ADT")
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


class CacheAtom(Generic[ANT, ADT]):
    '''Data cache without update'''

    def __init__(self, name: ANT, data: ADT, lifetime: CacheTimeout = 0):
        self.__lifetime: float = float(lifetime)
        self.__timestamp: float = time()
        self.__name: ANT = name
        self.__data: ADT = data

    def __str__(self) -> str:
        return f"cache object at {id(self)} name={self.name}"

    @property
    def up(self) -> float:
        return self.__timestamp

    @property
    def age(self) -> float:
        return time() - self.up

    @property
    def life(self) -> float:
        '''lifetime'''
        return self.__lifetime

    @property
    def down(self) -> float:
        '''countdown'''
        return self.life - self.age if self.life > 0.0 else 0.0

    @property
    def expired(self) -> bool:
        return self.life > 0.0 and self.age > self.life

    @property
    def name(self) -> ANT:
        return self.__name

    @property
    def data(self) -> ADT:
        return self.__data


class CacheItem(CacheAtom[INT, IDT]):
    '''Data cache with enforces expiration check'''

    def __init__(self, name: INT, data: IDT, lifetime: CacheTimeout = 0):
        super().__init__(name, data, lifetime)

    @property
    def data(self) -> IDT:
        if self.expired:
            raise CacheExpired(self.name)
        return super().data


class CachePool(Generic[PIT, PVT]):
    '''Data cache pool'''

    def __init__(self, lifetime: CacheTimeout = 0):
        self.__pool: Dict[PIT, CacheItem[PIT, PVT]] = {}
        self.__lifetime: float = float(lifetime)
        self.__intlock: Lock = Lock()  # internal lock

    def __str__(self) -> str:
        return f"cache pool at {id(self)}"

    def __len__(self) -> int:
        with self.__intlock:
            return len(self.__pool)

    def __iter__(self) -> Generator[PIT, Any, None]:
        with self.__intlock:
            yield from self.__pool

    def __contains__(self, index: PIT) -> bool:
        with self.__intlock:
            return index in self.__pool

    def __setitem__(self, index: PIT, value: PVT) -> None:
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
        with self.__intlock:
            self.__pool[index] = item

    def get(self, index: PIT) -> PVT:
        with self.__intlock:
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
        with self.__intlock:
            if index in self.__pool:
                del self.__pool[index]
