# coding:utf-8

from time import sleep
import unittest

from xkits import CacheAtom
from xkits import CacheData
from xkits import CacheExpired
from xkits import CacheItem
from xkits import CachePool
from ..cache import NamedCache


class test_cache(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.index = "test"
        cls.value = "unit"

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cache_atom(self):
        item = CacheAtom(self.value, 0.1)
        sleep(0.2)
        self.assertTrue(item.expired)
        self.assertLess(item.down, 0)
        self.assertEqual(item.data, self.value)
        item.data = "atom"
        self.assertEqual(item.data, "atom")

    def test_cache_data(self):
        def read(item: CacheData):
            return item.data
        item = CacheData(self.value, 0.1)
        sleep(0.2)
        self.assertTrue(item.expired)
        self.assertLess(item.down, 0)
        self.assertRaises(CacheExpired, read, item)
        item.data = "data"
        self.assertEqual(item.data, "data")

    def test_named_cache(self):
        item = NamedCache(self.index, self.value, 0.1)
        sleep(0.2)
        self.assertTrue(item.expired)
        self.assertLess(item.down, 0)
        self.assertEqual(item.data, self.value)
        item.data = "name"
        self.assertEqual(item.data, "name")

    def test_cache_item(self):
        def read(item: CacheItem):
            return item.data
        item = CacheItem(self.index, self.value, 0.1)
        sleep(0.2)
        self.assertTrue(item.expired)
        self.assertLess(item.down, 0)
        self.assertRaises(CacheExpired, read, item)
        item.data = "item"
        self.assertEqual(item.data, "item")

    def test_cache_pool(self):
        pool = CachePool()
        pool[self.index] = self.value
        self.assertEqual(pool[self.index], self.value)
        del pool[self.index]
        self.assertNotIn(self.index, pool)
