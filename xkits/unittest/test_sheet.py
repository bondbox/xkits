# coding:utf-8

import os
from tempfile import TemporaryDirectory
from typing import Union
import unittest

from xkits import csv
from xkits import form
from xkits import tabulate
from xkits import xls_reader
from xkits import xls_writer


class test_sheet(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.fake_form: form[str, Union[str, int]] = form(
            "scores", ["name", "score"])
        self.fake_form.extend([["alice", 90], ["cindy", 80]])
        self.fake_form.append(["eric", 70])

    def tearDown(self):
        pass

    def test_form(self):
        row = self.fake_form.new_row(["frank", 60])
        row.extend([None, 50])
        row.append("good")
        row[4] = "bad"
        self.fake_form[2] = row
        row[0].value = "garry"
        self.assertEqual(len(row), 5)
        self.assertFalse(row[3].empty)
        self.assertEqual(str(row[1]), "60")
        self.assertEqual(row[4].value, "bad")
        self.assertEqual(self.fake_form[2], row)
        self.assertEqual(len(self.fake_form), 3)
        self.assertEqual(self.fake_form.new_map(),
                         {"name": None, "score": None})

    def test_tabulate(self):
        print(tabulate(self.fake_form))

    def test_csv_header(self):
        with TemporaryDirectory() as thdl:
            path = os.path.join(thdl, "test.csv")
            csv.dump(path, self.fake_form)
            csv.load(path)

    def test_csv_no_header(self):
        self.fake_form.header = []
        with TemporaryDirectory() as thdl:
            path = os.path.join(thdl, "test.csv")
            csv.dump(path, self.fake_form)
            csv.load(path, include_header=False)

    def test_xls_header_sheet(self):
        with TemporaryDirectory() as thdl:
            path = os.path.join(thdl, "sheet", "test.xls")
            writer = xls_writer()
            writer.dump_sheet(self.fake_form)
            writer.save(path)
            reader = xls_reader(path)
            reader.load_sheet()
            self.assertEqual(reader.file, path)

    def test_xls_header_sheets(self):
        with TemporaryDirectory() as thdl:
            path = os.path.join(thdl, "sheets", "test.xls")
            writer = xls_writer()
            writer.dump_sheets([self.fake_form,
                                form("socre2", ["name", "score2"])])
            writer.save(path)
            reader = xls_reader(path)
            reader.load_sheets()
            self.assertEqual(reader.file, path)


if __name__ == "__main__":
    unittest.main()
