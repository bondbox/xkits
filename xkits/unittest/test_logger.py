# coding:utf-8

import unittest

from xkits import logger
import mock


class test_log(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.log = logger.log()

    def tearDown(self):
        pass

    def test_initiate_logger(self):
        self.log.initiate_logger(self.log.get_logger())

    @mock.patch.object(logger.os, "makedirs", mock.MagicMock())
    @mock.patch.object(logger.os.path, "isdir", mock.MagicMock(side_effect=[True]))  # noqa:E501
    @mock.patch.object(logger.os.path, "exists", mock.MagicMock(side_effect=[False]))  # noqa:E501
    @mock.patch.object(logger.os.path, "dirname", mock.MagicMock())
    @mock.patch.object(logger.logging, "FileHandler", mock.MagicMock())
    def test_new_file_handler(self):
        self.log.new_file_handler("unittest.log")


if __name__ == "__main__":
    unittest.main()
