# coding=utf-8

import os
from typing import List


def singleton(cls):
    instance = {}

    def _singleton_wrapper(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return _singleton_wrapper


@singleton
class chdir:
    '''Change working directory
    '''

    def __init__(self):
        self.__stack: List[str] = []

    def pushd(self, path: str):
        '''Add directory to stack.
        '''
        assert isinstance(path, str), f"type '{type(path)}' is not str"
        assert os.path.isdir(path), f"path '{path}' is not directory"
        self.__stack.append(os.getcwd())
        os.chdir(path)

    def popd(self):
        '''Remove directory from stack.
        '''
        assert len(self.__stack) > 0
        os.chdir(self.__stack.pop())
