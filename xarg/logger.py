#!/usr/bin/python3
# coding:utf-8

import enum


@enum.unique
class level(enum.IntEnum):
    FATAL = 1
    ERROR = 10
    WARN = 100
    INFO = 1000
    DEBUG = 10000
    TRACE = 20000


FATAL = level.FATAL
ERROR = level.ERROR
WARN = level.WARN
INFO = level.INFO
DEBUG = level.DEBUG
TRACE = level.TRACE


@enum.unique
class detail(enum.IntFlag):
    NONE = 0
    TIMESTAMP = 1 << 0
    PID = 1 << 1
    THREADID = 1 << 2
    THREADNAME = 1 << 3
    THREAD = THREADID | THREADNAME
    FILENAME = 1 << 6
    FUNCTION = 1 << 7
    FRAME = FILENAME | FUNCTION
    ALL = TIMESTAMP | PID | THREAD | FRAME


TIMESTAMP = detail.TIMESTAMP
PID = detail.PID
THREADID = detail.THREADID
THREADNAME = detail.THREADNAME
FILENAME = detail.FILENAME
FUNCTION = detail.FUNCTION
