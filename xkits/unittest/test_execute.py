# coding:utf-8

from time import sleep
import unittest

from xkits import hourglass


class test_execute(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @hourglass(0.5)
    def fake_hourglass(self, value: float = 1.0):
        return sleep(value)

    def test_hourglass(self):
        self.assertRaises(TimeoutError, self.fake_hourglass)
        self.assertIsNone(self.fake_hourglass(0.1))


if __name__ == "__main__":
    unittest.main()
