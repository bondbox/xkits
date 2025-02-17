# coding:utf-8

from base64 import b16decode
from base64 import b16encode
from configparser import ConfigParser
from errno import EPERM
import os
import shutil
import sys
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Union

from pip._internal.commands.show import _PackageInfo
from pip._internal.commands.show import search_packages_info
from tabulate import tabulate

from .actuator import add_command
from .actuator import commands
from .actuator import run_command
from .attribute import __prog_complete__
from .attribute import __project__
from .attribute import __urlhome__
from .attribute import __version__
from .parser import argp
from .utils import singleton

USER_BASH_COMPLETION_CFG = "~/.bash_completion"
USER_BASH_COMPLETION_DIR = "~/.bash_completion.d"


def enable_bash():

    def update_code():
        bash_completion_path = os.path.expanduser(USER_BASH_COMPLETION_CFG)
        bash_completion_hook = os.path.expanduser(USER_BASH_COMPLETION_DIR)
        bash_completion_code = """
for bcfile in ~/.bash_completion.d/* ; do
  source ${bcfile}
done
"""
        if not os.path.exists(bash_completion_hook):
            os.makedirs(bash_completion_hook)
        with open(bash_completion_path, "r", encoding="utf-8") as fh:
            if bash_completion_code in fh.read():
                return
        with open(bash_completion_path, "a", encoding="utf-8") as fh:
            fh.write(f"\n{bash_completion_code}\n")

    update_code()
    update_bash(__prog_complete__)


def update_bash(cmd: str) -> int:
    bash_completion_hook = os.path.expanduser(USER_BASH_COMPLETION_DIR)
    name = b16encode(cmd.encode()).decode()
    path = os.path.join(bash_completion_hook, f"{__prog_complete__}-{name}")
    return os.system(f"register-python-argcomplete {cmd} > {path}")


def remove_bash(cmd: str) -> bool:
    bash_completion_hook = os.path.expanduser(USER_BASH_COMPLETION_DIR)
    name = b16encode(cmd.encode()).decode()
    path = os.path.join(bash_completion_hook, f"{__prog_complete__}-{name}")
    if os.path.isfile(path):
        os.remove(path)
    return not os.path.exists(path)


def list_bash() -> Set[str]:
    cmds: Set[str] = set()
    bash_completion_hook = os.path.expanduser(USER_BASH_COMPLETION_DIR)
    if not os.path.exists(bash_completion_hook):
        os.makedirs(bash_completion_hook)
    for item in os.listdir(bash_completion_hook):
        if not os.path.isfile(os.path.join(bash_completion_hook, item)):
            continue
        keys = item.split("-", 1)
        if len(keys) == 2 and keys[0] == __prog_complete__:
            cmds.add(b16decode(keys[1]).decode())
    return cmds


@singleton
class collections:

    def __init__(self):
        self.__cmds: Set[str] = set()
        for _pkg in tuple({"argcomplete", __project__}):
            for _req in set(self.get_package_info(_pkg).required_by):
                config = ConfigParser()
                package_info = self.get_package_info(_req)
                config.read_string(os.linesep.join(package_info.entry_points))
                if config.has_section("console_scripts"):
                    for _cmd in config["console_scripts"]:
                        self.__cmds.add(_cmd)

    @property
    def cmds(self) -> Iterable[str]:
        return iter(self.__cmds)

    @classmethod
    def get_package_info(cls, package_name: str) -> _PackageInfo:
        return list(search_packages_info([package_name]))[0]


@add_command("enable", help="Enable completion.")
def add_cmd_enable(_arg: argp):
    pass


@run_command(add_cmd_enable)
def run_cmd_enable(cmds: commands) -> int:
    which = shutil.which("activate-global-python-argcomplete")
    command = f"{which} --user --yes"
    cmds.logger.info(command)
    retcode = os.system(command)
    if retcode != 0:
        return retcode
    enable_bash()
    return 0


@add_command("update", help="Update completion config.")
def add_cmd_update(_arg: argp):
    group_script = _arg.argument_group("Specify update command or script")
    group_script.add_argument("--script", type=str, nargs=1, metavar="PATH",
                              dest="_commands_", action="extend",
                              help="Specify script path.")
    group_script.add_argument(type=str, nargs="*", metavar="command",
                              dest="_commands_", action="extend",
                              help="Specify command.")


@run_command(add_cmd_update)
def run_cmd_update(cmds: commands) -> int:
    iter_commands = getattr(cmds.args, "_commands_")
    if len(iter_commands) == 0:
        iter_commands = collections().cmds
    for cmd in set(iter_commands):
        if shutil.which(cmd) is None:
            cmds.stderr(f"Non existent command or script: {cmd}")
            continue
        cmds.stdout(f"Update command or script: {cmd}")
        update_bash(cmd)
    cmds.stdout("Please restart your shell or source the file to activate it.")
    cmds.stdout(f"Bash: source {os.path.expanduser(USER_BASH_COMPLETION_CFG)}")
    return 0


@add_command("remove", help="Remove completion config.")
def add_cmd_remove(_arg: argp):
    allowed = list(list_bash())
    group_script = _arg.argument_group("Specify remove command or script")
    mgroup_script = group_script.add_mutually_exclusive_group()
    mgroup_script.add_argument("--auto-clean", dest="_clean_",
                               action="store_true",
                               help="Clean invalid commands or scripts.")
    mgroup_script.add_argument("--all", const=allowed,
                               dest="_commands_", action="store_const",
                               help="Remove all commands or scripts.")
    group_script.add_argument(type=str, nargs="*", metavar="command",
                              dest="_commands_", action="extend",
                              help="Specify command or script.",
                              choices=allowed + [[]])


@run_command(add_cmd_remove)
def run_cmd_remove(cmds: commands) -> int:
    list_commands: List[str] = getattr(cmds.args, "_commands_")
    if getattr(cmds.args, "_clean_"):
        assert isinstance(list_commands, list)
        for cmd in list_bash():
            if cmd in list_commands:
                continue
            if shutil.which(cmd) is None:
                list_commands.append(cmd)
    for cmd in set(list_commands):
        cmds.stdout(f"Remove command or script: {cmd}")
        assert remove_bash(cmd)
    return 0


@add_command("list", help="List all completion.")
def add_cmd_list(_arg: argp):
    pass


@run_command(add_cmd_list)
def run_cmd_list(cmds: commands) -> int:
    table: Dict[str, Dict[str, Union[None, str, Set[str]]]] = {}

    def update_table(cmd: str, shell: str):
        if cmd not in table:
            table[cmd] = {"which": shutil.which(cmd), "shell": set()}
        shell_set = table[cmd]["shell"]
        assert isinstance(shell_set, set)
        shell_set.add(shell)

    def output_table() -> List[Tuple[str, str, str]]:
        datas: List[Tuple[str, str, str]] = []
        for k, v in table.items():
            which = v["which"] if v["which"] is not None else "None"
            shell = v["shell"]
            assert isinstance(which, str)
            assert isinstance(shell, set)
            datas.append((k, which, ", ".join(shell)))
        datas.sort(key=lambda line: line[0])
        datas.insert(0, ("command", "which", "shell"))
        return datas

    for cmd in list_bash():
        update_table(cmd, "bash")
    cmds.stdout(tabulate(output_table(), headers="firstrow"))
    return 0


@add_command(__prog_complete__, description="Tab completion management.")
def add_cmd(_arg: argp):
    pass


@run_command(add_cmd, add_cmd_enable, add_cmd_update, add_cmd_remove,
             add_cmd_list)
def run_cmd(cmds: commands) -> int:
    if sys.version_info < (3, 8):
        cmds.logger.error("Require Python>=3.8")
        return EPERM
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {__urlhome__}.")  # noqa:E501
