# coding:utf-8

from time import sleep
from time import time
from typing import Optional
from typing import Union

TimeUnit = Union[float, int]


class TimeMeter():
    '''Timer'''

    def __init__(self, startup: bool = True, always: bool = False):
        timestamp: float = time()
        self.__always_running: bool = always
        self.__started: float = timestamp if startup else 0.0
        self.__created: float = timestamp
        self.__stopped: float = 0.0

    @property
    def created_time(self) -> float:
        return self.__created

    @property
    def started_time(self) -> float:
        return self.__started

    @property
    def stopped_time(self) -> float:
        return self.__stopped

    @property
    def runtime(self) -> float:
        return (self.stopped_time or time()) - self.started_time if self.started_time > 0.0 else 0.0  # noqa:E501

    @property
    def started(self) -> bool:
        '''running and not stopped'''
        return self.started_time > 0.0 and self.stopped_time == 0.0

    @property
    def stopped(self) -> bool:
        '''started and stopped'''
        return self.started_time > 0.0 and self.stopped_time > 0.0

    def restart(self):
        self.__started = time()
        self.__stopped = 0.0

    def startup(self):
        if not self.started:
            self.__started = time()
            self.__stopped = 0.0

    def shutdown(self):
        if self.__always_running:
            raise RuntimeError(f"TimeMeter({self}) cannot shutdown")

        if self.started:
            self.__stopped = time()

    def clock(self, delay: TimeUnit = 1.0):
        '''sleep for a while'''
        if self.started and delay > 0.0:
            sleep(delay)

    def alarm(self, endtime: TimeUnit):
        '''sleep until endtime'''
        if not self.started:
            self.startup()
        while (delta := endtime - self.runtime) > 0.0:
            self.clock(delta)

    def reset(self):
        self.__started = 0.0
        self.__stopped = 0.0


class DownMeter(TimeMeter):
    '''Countdown'''

    def __init__(self, lifetime: TimeUnit = 0.0, startup: bool = True):
        self.__lifetime: float = max(float(lifetime), 0.0)
        super().__init__(startup=startup, always=True)

    @property
    def lifetime(self) -> float:
        return self.__lifetime

    @property
    def downtime(self) -> float:
        return self.lifetime - self.runtime if self.lifetime > 0.0 else 0.0

    @property
    def expired(self) -> bool:
        return self.lifetime > 0.0 and self.runtime > self.lifetime

    def reset(self):
        super().restart()

    def renew(self, lifetime: Optional[TimeUnit] = None) -> None:
        '''renew timestamp and update lifetime(optional)'''
        if lifetime is not None:
            self.__lifetime = float(lifetime)
        super().restart()


class CountMeter():
    '''Counter'''

    def __init__(self, allow_sub: bool = False):
        self.__allow_sub: bool = allow_sub
        self.__total: int = 0

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({id(self)})"

    @property
    def total(self) -> int:
        return self.__total

    def inc(self, value: int = 1) -> int:
        if value <= 0:
            raise ValueError(f"{self} inc value({value}) must be greater than 0")  # noqa:E501
        self.__total += value
        return self.__total

    def dec(self, value: int = 1) -> int:
        if not self.__allow_sub:
            raise RuntimeError(f"{self} is not allow sub")
        if value <= 0:
            raise ValueError(f"{self} dec value({value}) must be greater than 0")  # noqa:E501
        self.__total -= value
        return self.__total


class StatusCountMeter(CountMeter):
    '''Counter for status'''

    def __init__(self):
        super().__init__(allow_sub=False)
        self.__success: int = 0
        self.__failure: int = 0

    @property
    def success(self) -> int:
        return self.__success

    @property
    def failure(self) -> int:
        return self.__failure

    def inc(self, success: bool = True) -> int:  # noqa:E501 pylint: disable=arguments-renamed
        def _success():
            self.__success += 1

        def _failure():
            self.__failure += 1

        _success() if success else _failure()  # noqa:E501 pylint: disable=expression-not-assigned
        return super().inc()

    def dec(self) -> int:  # pylint: disable=arguments-differ
        return self.inc(success=False)


class TsCountMeter(CountMeter):
    '''Counter with timestamp'''

    def __init__(self, allow_sub: bool = False):
        super().__init__(allow_sub=allow_sub)
        self.__created: float = time()
        self.__updated: float = 0.0

    @property
    def created_time(self) -> float:
        return self.__created

    @property
    def updated_time(self) -> float:
        return self.__updated

    def inc(self, value: int = 1) -> int:
        total: int = super().inc(value)
        self.__updated = time()
        return total

    def dec(self, value: int = 1) -> int:
        total: int = super().dec(value)
        self.__updated = time()
        return total
