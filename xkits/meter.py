# coding:utf-8

from time import sleep
from time import time
from typing import Optional
from typing import Union

TimeUnit = Union[float, int]


class TimeMeter():
    def __init__(self, start: bool = True):
        timestamp: float = time()
        self.__started: float = timestamp if start else 0.0
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
        return time() - self.started_time if self.started_time > 0.0 else 0.0

    @property
    def started(self) -> bool:
        return self.started_time > 0.0 and self.stopped_time == 0.0

    def restart(self):
        self.__started = time()
        self.__stopped = 0.0

    def startup(self):
        if not self.started:
            self.__started = time()

    def shutdown(self):
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
    def __init__(self, lifetime: TimeUnit = 0.0):
        self.__lifetime: float = max(float(lifetime), 0.0)
        super().__init__(start=True)

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
        self.restart()

    def renew(self, lifetime: Optional[TimeUnit] = None) -> None:
        '''renew timestamp and update lifetime(optional)'''
        if lifetime is not None:
            self.__lifetime = float(lifetime)
        self.restart()

    def shutdown(self):
        raise RuntimeError("DownMeter cannot shutdown")
