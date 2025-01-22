# coding:utf-8

import unittest

from xkits import chdir


class test_chdir(unittest.TestCase):

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

    def test_chdir(self):
        self.assertRaises(AssertionError, chdir().popd)
        chdir().pushd("xkits")
        chdir().pushd("unittest")
        chdir().popd()
        chdir().popd()
        self.assertRaises(AssertionError, chdir().popd)


if __name__ == "__main__":
    unittest.main()
