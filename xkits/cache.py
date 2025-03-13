# coding:utf-8

from threading import Lock
from time import time
from typing import Any
from typing import Dict
from typing import Generic
from typing import Iterator
from typing import Optional
from typing import TypeVar
from typing import Union

CacheTimeUnit = Union[float, int]


class CacheLookupError(LookupError):
    pass


class CacheMiss(CacheLookupError):
    def __init__(self, name: Any):
        super().__init__(f"Not found {name} in cache")


class CacheExpired(CacheLookupError):
    def __init__(self, name: Optional[Any] = None):
        super().__init__("Cache expired" if name is None else f"Cache {name} expired")  # noqa:E501


CADT = TypeVar("CADT")


class CacheAtom(Generic[CADT]):
    '''Data cache without name'''

    def __init__(self, data: CADT, lifetime: CacheTimeUnit = 0):
        self.__lifetime: float = float(lifetime)
        self.__uptime: float = time()
        self.__data: CADT = data

    def __str__(self) -> str:
        return f"cache object at {id(self)}"

    @property
    def up(self) -> float:
        '''uptime'''
        return self.__uptime

    @property
    def age(self) -> float:
        '''runtime'''
        return time() - self.up

    @property
    def life(self) -> float:
        '''lifetime'''
        return self.__lifetime

    @property
    def down(self) -> float:
        '''downtime'''
        return self.life - self.age if self.life > 0.0 else 0.0

    @property
    def expired(self) -> bool:
        return self.life > 0.0 and self.age > self.life

    def renew(self, lifetime: Optional[CacheTimeUnit] = None) -> None:
        '''renew uptime and lifetime(optional)'''
        if lifetime is not None:
            self.__lifetime = float(lifetime)
        self.__uptime = time()

    def update(self, data: CADT) -> None:
        '''update cache data'''
        self.__data = data
        self.renew()

    @property
    def data(self) -> CADT:
        return self.__data

    @data.setter
    def data(self, data: CADT) -> None:
        self.update(data)


CDT = TypeVar("CDT")


class CacheData(CacheAtom[CDT]):
    '''Data cache with enforces expiration check'''

    @property
    def data(self) -> CDT:
        if self.expired:
            raise CacheExpired()
        return super().data

    @data.setter
    def data(self, data: CDT) -> None:
        super().update(data)


NCNT = TypeVar("NCNT")
NCDT = TypeVar("NCDT")


class NamedCache(CacheAtom[NCDT], Generic[NCNT, NCDT]):
    '''Named data cache'''

    def __init__(self, name: NCNT, data: NCDT, lifetime: CacheTimeUnit = 0):
        super().__init__(data, lifetime)
        self.__name: NCNT = name

    def __str__(self) -> str:
        return f"cache object at {id(self)} name={self.name}"

    @property
    def name(self) -> NCNT:
        return self.__name


CINT = TypeVar("CINT")
CIDT = TypeVar("CIDT")


class CacheItem(NamedCache[CINT, CIDT]):
    '''Named data cache with enforces expiration check'''

    def __init__(self, name: CINT, data: CIDT, lifetime: CacheTimeUnit = 0):
        super().__init__(name, data, lifetime)

    @property
    def data(self) -> CIDT:
        if self.expired:
            raise CacheExpired(self.name)
        return super().data

    @data.setter
    def data(self, data: CIDT) -> None:
        super().update(data)


IPKT = TypeVar("IPKT")
IPVT = TypeVar("IPVT")


class ItemPool(Generic[IPKT, IPVT]):
    '''Cache item pool'''

    def __init__(self, lifetime: CacheTimeUnit = 0):
        self.__pool: Dict[IPKT, CacheItem[IPKT, IPVT]] = {}
        self.__lifetime: float = float(lifetime)
        self.__intlock: Lock = Lock()  # internal lock

    def __str__(self) -> str:
        return f"cache item pool at {id(self)}"

    def __len__(self) -> int:
        with self.__intlock:
            return len(self.__pool)

    def __iter__(self) -> Iterator[IPKT]:
        with self.__intlock:
            return iter(self.__pool.keys())

    def __contains__(self, index: IPKT) -> bool:
        with self.__intlock:
            return index in self.__pool

    def __setitem__(self, index: IPKT, value: IPVT) -> None:
        return self.put(index, value)

    def __getitem__(self, index: IPKT) -> CacheItem:
        return self.get(index)

    def __delitem__(self, index: IPKT) -> None:
        return self.delete(index)

    @property
    def lifetime(self) -> float:
        return self.__lifetime

    def put(self, index: IPKT, value: IPVT, lifetime: Optional[CacheTimeUnit] = None) -> None:  # noqa:E501
        life = lifetime if lifetime is not None else self.lifetime
        item = CacheItem(index, value, life)
        with self.__intlock:
            self.__pool[index] = item

    def get(self, index: IPKT) -> CacheItem:
        with self.__intlock:
            try:
                return self.__pool[index]
            except KeyError as exc:
                raise CacheMiss(index) from exc

    def delete(self, index: IPKT) -> None:
        with self.__intlock:
            if index in self.__pool:
                del self.__pool[index]


CPIT = TypeVar("CPIT")
CPVT = TypeVar("CPVT")


class CachePool(ItemPool[CPIT, CPVT]):
    '''Named data cache pool'''

    def __init__(self, lifetime: CacheTimeUnit = 0):
        super().__init__(lifetime=lifetime)

    def __str__(self) -> str:
        return f"cache pool at {id(self)}"

    def __getitem__(self, index: CPIT) -> CPVT:
        return self.get(index)

    def get(self, index: CPIT) -> CPVT:
        try:
            return super().get(index).data
        except CacheExpired as exc:
            super().delete(index)
            assert index not in self
            raise CacheMiss(index) from exc
