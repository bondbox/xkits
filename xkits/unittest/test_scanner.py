#!/usr/bin/python3
# coding:utf-8

import os
import shutil
import unittest

from xkits import scanner


def handler(obj: scanner.object) -> bool:
    return isinstance(obj, scanner.object)


class test_scanner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.scanner = scanner.load(paths=[os.path.join("xkits")],
                                   exclude=[os.path.join("xkits", "test")],
                                   handler=handler)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_load(self):
        self.assertIsInstance(scanner.load(paths=[os.path.join("scanloader")], handler=handler), scanner)  # noqa:E501

    def test_iter(self):
        for object in self.scanner:
            self.assertIsInstance(object, scanner.object)
            self.assertIsInstance(object.path, str)
            self.assertIsInstance(object.abspath, str)
            self.assertIsInstance(object.realpath, str)
            self.assertIsInstance(object.uid, int)
            self.assertIsInstance(object.gid, int)
            self.assertIsInstance(object.mode, int)
            self.assertIsInstance(object.size, int)
            self.assertIsInstance(object.ctime, float)
            self.assertIsInstance(object.atime, float)
            self.assertIsInstance(object.mtime, float)
            self.assertIsInstance(object.isdir, bool)
            self.assertIsInstance(object.isfile, bool)
            self.assertIsInstance(object.islink, bool)

            if object.isfile and not object.issym:
                self.assertIsInstance(object.md5, str)
                self.assertIsInstance(object.sha1, str)
                self.assertIsInstance(object.sha256, str)

    def test_dirs(self):
        for object in self.scanner.dirs:
            self.assertTrue(object.isdir)

    def test_files(self):
        for object in self.scanner.files:
            self.assertTrue(object.isfile)
            self.assertTrue(object.isreg)

    def test_links(self):
        for object in self.scanner.links:
            self.assertTrue(object.issym)

    def test_add_dir_object(self):
        object = scanner.object("test")
        self.scanner.add(object)
        self.assertIs(self.scanner["test"], object)

    def test_add_sym_object(self):
        path = shutil.which("python")
        if path:
            object = scanner.object(path)
            self.scanner.add(object)
            self.assertIs(self.scanner[path], object)

    def test_add_file_object(self):
        path = os.path.join("test", "requirements.txt")
        object = scanner.object(path)
        self.scanner.add(object)
        self.assertIs(self.scanner[path], object)


if __name__ == "__main__":
    unittest.main()
