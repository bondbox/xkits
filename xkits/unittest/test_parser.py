# coding:utf-8

from argparse import Namespace
import sys
import unittest

import mock

from xkits import argp


class test_argp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.argp = argp("xkits-test")

    def tearDown(self):
        pass

    @mock.patch.object(sys, "exit")
    def test_help_optional_h(self, mock_exit: mock.Mock):
        mock_exit.side_effect = [Exception("xkits-test")]
        self.assertRaises(Exception, self.argp.parse_args, "-h".split())
        mock_exit.assert_called_once_with(0)

    @mock.patch.object(sys, "exit")
    def test_help_optional_help(self, mock_exit: mock.Mock):
        mock_exit.side_effect = [Exception("xkits-test")]
        self.assertRaises(Exception, self.argp.parse_args, "--help".split())
        mock_exit.assert_called_once_with(0)

    def test_argument_group(self):
        group1 = self.argp.argument_group("test")
        group2 = self.argp.argument_group("test")
        self.assertEqual(group1, group2)

    def test_filter_optional_name(self):
        self.argp.add_opt_on("--debug")
        ret = self.argp.filter_optional_name("-d", "--debug")
        self.assertSequenceEqual(ret, ["-d"])

    def test_add_pos(self):
        self.argp.add_pos("path", type=str, nargs="+")
        args = self.argp.parse_args("test.py 123.txt".split())
        self.assertIsInstance(args, Namespace)
        self.assertIsInstance(args.path, list)
        self.assertEqual(args.path, ["test.py", "123.txt"])

    def test_add_opt(self):
        self.argp.add_opt("-v", "--value", type=int, nargs=1)
        args = self.argp.parse_args("--value 100".split())
        self.assertIsInstance(args, Namespace)
        self.assertIsInstance(args.value, int)
        self.assertEqual(args.value, 100)

    def test_add_opt_on_close(self):
        self.argp.add_opt_on("--dry-run")
        args = self.argp.parse_args("".split())
        self.assertIsInstance(args, Namespace)
        self.assertIsInstance(args.dry_run, bool)
        self.assertEqual(args.dry_run, False)

    def test_add_opt_on_open(self):
        self.argp.add_opt_on("--dry-run")
        args = self.argp.parse_args("--dry-run".split())
        self.assertIsInstance(args, Namespace)
        self.assertIsInstance(args.dry_run, bool)
        self.assertEqual(args.dry_run, True)

    def test_add_opt_off_close(self):
        self.argp.add_opt_off("--no-check")
        args = self.argp.parse_args("".split())
        self.assertIsInstance(args, Namespace)
        self.assertIsInstance(args.no_check, bool)
        self.assertEqual(args.no_check, True)

    def test_add_opt_off_open(self):
        self.argp.add_opt_off("--no-check")
        args = self.argp.parse_args("--no-check".split())
        self.assertIsInstance(args, Namespace)
        self.assertIsInstance(args.no_check, bool)
        self.assertEqual(args.no_check, False)

    def test_add_subparsers(self):
        _sub = self.argp.add_subparsers(dest="sub")
        _arg = _sub.add_parser("list")
        _arg.add_opt_on("-d", "--debug")
        args = self.argp.parse_args("list --debug".split())
        self.assertIsInstance(args, Namespace)
        self.assertIsInstance(args.sub, str)
        self.assertEqual(args.sub, "list")
        self.assertIsInstance(args.debug, bool)
        self.assertEqual(args.debug, True)


if __name__ == "__main__":
    unittest.main()
