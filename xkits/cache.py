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

CacheTimeout = Union[float, int]


class CacheLookup(LookupError):
    pass


class CacheMiss(CacheLookup):
    def __init__(self, name: Any):
        super().__init__(f"Not found {name} in cache")


class CacheExpired(CacheLookup):
    def __init__(self, name: Optional[Any] = None):
        super().__init__("Cache expired" if name is None else f"Cache {name} expired")  # noqa:E501


CADT = TypeVar("CADT")


class CacheAtom(Generic[CADT]):
    '''Data cache without name'''

    def __init__(self, data: CADT, lifetime: CacheTimeout = 0):
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

    def renew(self, lifetime: Optional[CacheTimeout] = None) -> None:
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

    def __init__(self, name: NCNT, data: NCDT, lifetime: CacheTimeout = 0):
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

    def __init__(self, name: CINT, data: CIDT, lifetime: CacheTimeout = 0):
        super().__init__(name, data, lifetime)

    @property
    def data(self) -> CIDT:
        if self.expired:
            raise CacheExpired(self.name)
        return super().data

    @data.setter
    def data(self, data: CIDT) -> None:
        super().update(data)


CPIT = TypeVar("CPIT")
CPVT = TypeVar("CPVT")


class CachePool(Generic[CPIT, CPVT]):
    '''Data cache pool'''

    def __init__(self, lifetime: CacheTimeout = 0):
        self.__pool: Dict[CPIT, CacheItem[CPIT, CPVT]] = {}
        self.__lifetime: float = float(lifetime)
        self.__intlock: Lock = Lock()  # internal lock

    def __str__(self) -> str:
        return f"cache pool at {id(self)}"

    def __len__(self) -> int:
        with self.__intlock:
            return len(self.__pool)

    def __iter__(self) -> Iterator[CPIT]:
        with self.__intlock:
            return iter(self.__pool.keys())

    def __contains__(self, index: CPIT) -> bool:
        with self.__intlock:
            return index in self.__pool

    def __setitem__(self, index: CPIT, value: CPVT) -> None:
        return self.put(index, value)

    def __getitem__(self, index: CPIT) -> CPVT:
        return self.get(index)

    def __delitem__(self, index: CPIT) -> None:
        return self.delete(index)

    @property
    def lifetime(self) -> float:
        return self.__lifetime

    def put(self, index: CPIT, value: CPVT, lifetime: Optional[CacheTimeout] = None) -> None:  # noqa:E501
        life = lifetime if lifetime is not None else self.lifetime
        item = CacheItem(index, value, life)
        with self.__intlock:
            self.__pool[index] = item

    def get(self, index: CPIT) -> CPVT:
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

    def delete(self, index: CPIT) -> None:
        with self.__intlock:
            if index in self.__pool:
                del self.__pool[index]
