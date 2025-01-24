# coding:utf-8

from argparse import Namespace
from errno import EINTR
from errno import ENOENT
import os
import sys
from tempfile import TemporaryDirectory
from typing import Tuple
import unittest

import mock

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import end_command
from xkits import pre_command
from xkits import run_command
from xkits.attribute import __version__


@add_command("debug", help="test logger level")
def add_cmd_debug(_arg: argp):
    commands().stdout("debug")
    _arg.add_opt_on("-d", "--debug")


@run_command(add_cmd_debug)
def run_cmd_debug(cmds: commands) -> int:
    cmds.logger.debug("debug")
    return 0


@add_command("known", help="test preparse")
def add_cmd_known(_arg: argp):
    commands().stdout("known")
    _arg.preparse_from_sys_argv()


@run_command(add_cmd_known)
def run_cmd_known(cmds: commands) -> int:
    cmds.logger.debug("known")
    return 0


@add_command("list", description="test list")
def add_cmd_list(_arg: argp):
    commands().stdout("list")


@run_command(add_cmd_list, add_cmd_debug, add_cmd_known)
def run_cmd_list(cmds: commands) -> int:
    cmds.logger.info("list")
    return 0


@add_command("incomplete", help="test incomplete")
def add_cmd_incomplete(_arg: argp):
    commands().stderr("error")


@run_command(add_cmd_incomplete)
def run_cmd_incomplete(cmds: commands) -> int:
    cmds.logger.error("incomplete")
    return -1


@add_command("keyboard", help="test KeyboardInterrupt")
def add_cmd_keyboard(_arg: argp):
    commands().stdout("keyboard")


@run_command(add_cmd_keyboard)
def run_cmd_keyboard(cmds: commands) -> int:
    cmds.logger.error("keyboard")
    raise KeyboardInterrupt


@add_command("exception", help="test BaseException")
def add_cmd_exception(_arg: argp):
    commands().stdout("exception")


@run_command(add_cmd_exception)
def run_cmd_exception(cmds: commands) -> int:
    cmds.logger.error("exception")
    raise BaseException


@add_command("prepare", help="test prepare")
def add_cmd_prepare(_arg: argp):
    commands().stdout("prepare")


@run_command(add_cmd_prepare)
def run_cmd_prepare(cmds: commands) -> int:
    return 0


@pre_command(run_cmd_prepare)
def pre_cmd_prepare(cmds: commands) -> int:
    cmds.logger.info("prepare")
    return -1


@add_command("purge", help="test purge")
def add_cmd_purge(_arg: argp):
    commands().stdout("purge")


@run_command(add_cmd_purge)
def run_cmd_purge(cmds: commands) -> int:
    return 0


@end_command(run_cmd_purge)
def end_cmd_purge(cmds: commands) -> int:
    cmds.logger.info("purge")
    return 1


@add_command("example", description="example")
def add_cmd(_arg: argp):
    commands().stdout("test")


@run_command(add_cmd, add_cmd_list, add_cmd_incomplete,
             add_cmd_keyboard, add_cmd_exception,
             add_cmd_prepare, add_cmd_purge)
def run_cmd(cmds: commands) -> int:
    cmds.logger.debug("main")
    return 0


@pre_command(run_cmd)
def pre_cmd(cmds: commands) -> int:
    cmds.logger.debug("prepare")
    return 0


@end_command(run_cmd)
def end_cmd(cmds: commands) -> int:
    cmds.logger.debug("purge")
    return 0


class test_commands(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.cmds = commands()

    def tearDown(self):
        pass

    @mock.patch.object(sys, "exit")
    def test_help_action(self, mock_exit: mock.Mock):
        mock_exit.side_effect = [Exception("xkits-test")]
        self.assertRaises(Exception, self.cmds.run, add_cmd, "--help".split())
        mock_exit.assert_called_once_with(0)

    @mock.patch.object(sys, "exit")
    def test_help_action_h(self, mock_exit: mock.Mock):
        mock_exit.side_effect = [Exception("xkits-test")]
        self.assertRaises(Exception, self.cmds.run, add_cmd, "-h".split())
        mock_exit.assert_called_once_with(0)

    @mock.patch.object(sys, "exit")
    def test_version_action(self, mock_exit: mock.Mock):
        self.cmds.version = __version__
        mock_exit.side_effect = [Exception("xkits-test")]
        self.assertRaises(Exception, self.cmds.run, add_cmd,
                          "--version".split())
        mock_exit.assert_called_once_with(0)

    def test_version_debug(self):
        self.cmds.version = __version__
        ret = self.cmds.run(argv="--stderr --debug".split())
        self.assertEqual(ret, 0)

    def test_root(self):
        self.assertIsInstance(self.cmds.root, add_command)
        assert isinstance(self.cmds.root, add_command)
        self.assertIs(self.cmds.root.cmds, self.cmds)
        self.assertIsInstance(self.cmds.root.bind, run_command)
        assert isinstance(self.cmds.root.bind, run_command)
        self.assertIsInstance(self.cmds.root.bind.bind, add_command)
        self.assertIs(self.cmds.root.bind.bind, self.cmds.root)
        if self.cmds.root.bind.prep:
            self.assertIsInstance(self.cmds.root.bind.prep, pre_command)
            self.assertIs(self.cmds.root.bind.prep.main, self.cmds.root.bind)
        if self.cmds.root.bind.done:
            self.assertIsInstance(self.cmds.root.bind.done, end_command)
            self.assertIs(self.cmds.root.bind.done.main, self.cmds.root.bind)
        self.assertIsInstance(self.cmds.root.subs, Tuple)
        assert isinstance(self.cmds.root.subs, Tuple)
        for _sub in self.cmds.root.subs:
            self.assertIsInstance(_sub, add_command)
            self.assertIs(_sub.root, self.cmds.root)
            self.assertIs(_sub.prev, self.cmds.root)
            self.assertIsInstance(_sub.bind, run_command)
            assert isinstance(_sub.bind, run_command)
            if _sub.bind.prep:
                self.assertIsInstance(_sub.bind.prep, pre_command)
                self.assertIs(_sub.bind.prep.main, _sub.bind)
            if _sub.bind.done:
                self.assertIsInstance(_sub.bind.done, end_command)
                self.assertIs(_sub.bind.done.main, _sub.bind)
            if _sub.subs:
                for _son in _sub.subs:
                    self.assertIsInstance(_son, add_command)
                    self.assertIs(_son.root, self.cmds.root)
                    self.assertIs(_son.prev, _sub)

    def test_parse_root(self):
        ret = self.cmds.parse(argv="--stdout --debug".split())
        self.assertIsInstance(ret, Namespace)

    def test_run_root_error(self):
        ret = self.cmds.run(mock.Mock(), argv="--stdout -d".split())
        self.assertEqual(ret, ENOENT)

    def test_run_KeyboardInterrupt(self):
        ret = self.cmds.run(argv="keyboard --stderr -d".split())
        self.assertEqual(ret, EINTR)

    def test_run_BaseException(self):
        with TemporaryDirectory() as _tmp:
            path = os.path.join(_tmp, "log.txt")
            ret = self.cmds.run(argv=f"exception --log {path}".split())
            self.assertEqual(ret, 10000)

    def test_run_prepare(self):
        ret = self.cmds.run(argv="prepare --stdout --debug".split())
        self.assertEqual(ret, -1)

    def test_run_purge(self):
        ret = self.cmds.run(argv="purge --stderr --debug".split())
        self.assertEqual(ret, 1)

    @mock.patch.object(argp, "filter_optional_name")
    def test_filter_optional_name(self, mock_filter_optional_name: mock.Mock):
        mock_filter_optional_name.return_value = []
        ret = self.cmds.run(add_cmd, [], prog="example",
                            description="unittest")
        self.assertEqual(ret, 0)

    def test_has_sub(self):
        ret = self.cmds.has_sub(add_cmd)
        self.assertIsInstance(ret, bool)

    def test_subcommand_list(self):
        ret = self.cmds.run(add_cmd, "incomplete".split(), prog="example")
        self.assertEqual(ret, -1)


class test_commands_logger(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.cmds = commands()

    def tearDown(self):
        pass

    def test_disable_logger(self):
        self.cmds.enabled_logger = False
        ret = self.cmds.run(argv=[])
        self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()
