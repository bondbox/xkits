# coding:utf-8

from time import sleep
import unittest

from xkits import CacheAtom
from xkits import CacheData
from xkits import CacheExpired
from xkits import CacheItem
from xkits import CacheMiss
from xkits import CachePool
from xkits import NamedCache


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
        self.assertFalse(item.expired)
        self.assertGreater(item.down, 0)
        self.assertEqual(item.data, self.value)
        sleep(0.2)
        self.assertTrue(item.expired)
        self.assertLess(item.down, 0)
        self.assertEqual(item.data, self.value)
        item.renew(0.5)
        self.assertFalse(item.expired)
        self.assertGreater(item.down, 0)
        self.assertEqual(item.data, self.value)
        item.data = "atom"
        self.assertEqual(item.data, "atom")
        self.assertEqual(str(item), f"cache object at {id(item)}")

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
        self.assertEqual(str(item), f"cache object at {id(item)} name={item.name}")  # noqa:E501

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
        def read(pool: CachePool, name: str):
            return pool[name]
        pool: CachePool[str, str] = CachePool()
        pool[self.index] = self.value
        self.assertEqual(len(pool), 1)
        self.assertEqual(pool[self.index], self.value)
        for key in pool:
            self.assertIsInstance(pool[key], str)
        del pool[self.index]
        self.assertNotIn(self.index, pool)
        self.assertRaises(CacheMiss, read, pool, self.index)
        self.assertEqual(len(pool), 0)
        self.assertEqual(str(pool), f"cache pool at {id(pool)}")

    def test_cache_pool_timeout(self):
        def read(pool: CachePool, name: str):
            return pool[name]
        pool = CachePool(0.1)
        pool[self.index] = self.value
        self.assertEqual(pool[self.index], self.value)
        sleep(0.2)
        self.assertEqual(len(pool), 1)
        self.assertRaises(CacheMiss, read, pool, self.index)
        self.assertEqual(len(pool), 0)


if __name__ == "__main__":
    unittest.main()
