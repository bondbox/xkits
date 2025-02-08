# coding:utf-8

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as ThreadTimeout
from typing import Callable
from typing import Union

ExecuteTimeUnit = Union[float, int]


class Executor():  # pylint: disable=too-few-public-methods
    def __init__(self, fn: Callable, *args, **kwargs) -> None:
        self.__fn = fn
        self.__args = args
        self.__kwargs = kwargs

    def countdown(self, seconds: ExecuteTimeUnit):
        with ThreadPoolExecutor() as executor:
            try:
                future = executor.submit(self.__fn, *self.__args, **self.__kwargs)  # noqa:E501
                return future.result(seconds)
            except ThreadTimeout as exc:
                message: str = f"Run timeout of {seconds} seconds"
                raise TimeoutError(message) from exc


def hourglass(seconds: ExecuteTimeUnit):
    def decorator(fn):
        def inner(*args, **kwargs):
            return Executor(fn, *args, **kwargs).countdown(seconds)
        return inner
    return decorator
