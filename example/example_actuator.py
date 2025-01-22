#!/usr/bin/python3
# coding:utf-8

from typing import List
from typing import Optional

from xkits import add_command
from xkits import argp
from xkits import commands
from xkits import run_command


@add_command('key', help="item key")
def cmd_key(_arg: argp):
    pass


@add_command('value', help="item value")
def cmd_val(_arg: argp):
    pass


@add_command('get', help="get item")
def cmd_get(_arg: argp):
    pass


@run_command(cmd_get, cmd_key)
def run_get(args) -> int:
    print("run get", args)
    return 0


@add_command('set', help="set item")
def cmd_set(_arg: argp):
    pass


@run_command(cmd_set, cmd_key, cmd_val)
def run_set(args) -> int:
    print("run set", args)
    return 0


@add_command('del', help="delete item")
def cmd_del(_arg: argp):
    pass


@run_command(cmd_del)
def run_del(args) -> int:
    print("run del", args)
    return 0


@add_command('example')
def cmd(_arg: argp):
    _arg.add_opt_on('--debug')
    _arg.add_opt_on('-t', '--test')
    _arg.add_opt_off('-s', '--show')


@run_command(cmd, cmd_get, cmd_set, cmd_del)
def run(args) -> int:
    print("run example", args)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    return commands().run(
        argv=argv,
        prog="xkits-example",
        description="Simple command-line tool based on argparse.")


if __name__ == '__main__':
    main()
