# coding:utf-8

from grp import getgrgid
import os
from pwd import getpwuid
from tempfile import TemporaryDirectory
import unittest

from xkits import safile
from xkits import stfile


class test_stfile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tdir = TemporaryDirectory()
        cls.path = os.path.join(cls.tdir.name, "unittest")
        with open(cls.path, "w") as whdl:
            whdl.write("unittest")
        cls.file = stfile(cls.path)
        cls.username = getpwuid(os.getuid()).pw_name
        cls.groupname = getgrgid(os.getgid()).gr_name

    @classmethod
    def tearDownClass(cls):
        cls.tdir.cleanup()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_check_file(self):
        self.assertEqual(self.file.path, self.path)
        self.assertIsInstance(self.file.stat, os.stat_result)
        self.file.username = self.username
        self.file.groupname = self.groupname
        self.assertEqual(self.file.uid, os.getuid())
        self.assertEqual(self.file.gid, os.getgid())
        self.assertEqual(self.file.username, self.username)
        self.assertEqual(self.file.groupname, self.groupname)
        self.file.chmod("777")
        self.assertEqual(self.file.mode, "100777")
        self.assertEqual(self.file.human_file_type, "-")
        self.assertEqual(self.file.human_mode, "-rwxrwxrwx")
        self.assertEqual(self.file.human_owner_permissions, "rwx")
        self.assertEqual(self.file.human_group_permissions, "rwx")
        self.assertEqual(self.file.human_other_permissions, "rwx")
        self.file.chown(str(self.file.uid))
        self.file.chown(self.username)
        self.file.chown(self.file.uid)
        self.file.chgrp(str(self.file.gid))
        self.file.chgrp(self.groupname)
        self.file.chgrp(self.file.gid)


class test_safile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = "ZbbwpP4%oSwYxP=t+LkyXXzqL9fE8!"

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_backup_and_restore(self):
        with TemporaryDirectory() as thdl:
            path = os.path.join(thdl, "test")
            self.assertTrue(safile.create_backup(path))
            with open(path, "w") as whdl:
                whdl.write(self.text)
            self.assertTrue(safile.create_backup(path, copy=True))
            self.assertTrue(safile.create_backup(path))
            with open(path, "w") as whdl:
                whdl.write("unittest")
            self.assertTrue(safile.restore(path))
            with open(path, "r") as rhdl:
                self.assertEqual(rhdl.read(), self.text)
            self.assertTrue(safile.create_backup(path, copy=False))
            self.assertTrue(safile.delete_backup(path))


if __name__ == "__main__":
    unittest.main()
