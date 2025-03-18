# coding:utf-8

from argparse import ArgumentParser
from argparse import Namespace
from argparse import _ArgumentGroup  # noqa:H306
from argparse import _HelpAction
from argparse import _SubParsersAction
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple

from xkits.attribute import __project__
from xkits.attribute import __urlhome__

try:
    from argcomplete import autocomplete
except ModuleNotFoundError:  # pragma: no cover
    pass  # pragma: no cover


class checker():

    prefix_chars = "-"

    @classmethod
    def check_name_pos(cls, fn):
        '''check positional argument name
        '''

        def inner(self, name: str, **kwargs):
            assert isinstance(name, str) and name[0] not in cls.prefix_chars, \
                f"{name} is not a positional argument name"
            return fn(self, name, **kwargs)

        return inner

    @classmethod
    def check_name_opt(cls, fn):
        '''check optional argument name
        '''

        def inner(self, *name: str, **kwargs):
            # 1. check short form optional argument ("-x")
            # 2. check long form optional argument ("--xx")
            # 3. only short form or long form or short form + long form
            # 模棱两可的数据（-1可以是一个负数的位置参数）
            for n in name:
                assert isinstance(n, str) and n[0] in cls.prefix_chars, \
                    f"{n} is not an optional argument name"
            return fn(self, *name, **kwargs)

        return inner

    @classmethod
    def check_nargs_opt(cls, fn):
        '''nargs hook function:
            nargs < -1: using "?", 0 or 1 argument, default value
            nargs = -1: using "+", arguments list, at least 1
            nargs = 0: using "*", arguments list, allow to be empty
            nargs = 1: redirect to "?", 0 or 1 argument
            nargs > 1: N arguments list
        '''

        def inner(self, *args, **kwargs):
            _nargs = kwargs.get("nargs", -2)
            if isinstance(_nargs, int) and _nargs < 2:
                _nargs = {1: "?", 0: "*", -1: "+"}.get(_nargs, "?")
            kwargs.update({"nargs": _nargs})
            return fn(self, *args, **kwargs)

        return inner


class argp(ArgumentParser):
    '''Simple command-line tool based on argparse.
    '''

    def __init__(self,  # pylint: disable=R0913,R0917
                 argv: Optional[Sequence[str]] = None,
                 prog: Optional[str] = None,
                 usage: Optional[str] = None,
                 prev_parser: Optional["argp"] = None,
                 description: Optional[str] = f"Command-line based on {__project__}.",  # noqa:E501
                 epilog: Optional[str] = f"For more, please visit {__urlhome__}",  # noqa:E501
                 **kwargs):
        kwargs.setdefault("prog", prog)
        kwargs.setdefault("usage", usage)
        kwargs.setdefault("description", description)
        kwargs.setdefault("epilog", epilog)
        ArgumentParser.__init__(self, **kwargs)
        self.__argv: Optional[Sequence[str]] = argv
        self.__help_option: Dict[str, _HelpAction] = {}
        self.__prev_parser: argp = prev_parser or self
        self.__next_parser: List[argp] = []
        if prev_parser is not None:
            prev_parser.next_parser.append(self)

    @property
    def argv(self) -> Optional[Sequence[str]]:
        root = self.root_parser
        return root.argv if root is not self else self.__argv

    @property
    def prev_parser(self) -> "argp":
        return self.__prev_parser

    @property
    def next_parser(self) -> List["argp"]:
        return self.__next_parser

    @property
    def root_parser(self) -> "argp":
        root = self.prev_parser
        while root.prev_parser != root:
            root = root.prev_parser
        return root

    def argument_group(self,
                       title: Optional[str] = None,
                       description: Optional[str] = None,
                       **kwargs) -> _ArgumentGroup:
        '''Find the created argument group by title, create if not exist.
        '''
        for group in self._action_groups:
            if title == group.title:
                return group
        return self.add_argument_group(title, description, **kwargs)

    @checker.check_name_opt
    def filter_optional_name(self, *name: str) -> Sequence[str]:
        '''Filter defined optional argument name.
        '''
        option_strings: Set[str] = set()
        for action in self._get_optional_actions():
            option_strings.update(action.option_strings)
        return [n for n in name if n not in option_strings]

    @checker.check_name_pos
    def add_pos(self, name: str, **kwargs) -> None:
        '''Add positional argument.
        '''
        assert "dest" not in kwargs, \
            "dest supplied twice for positional argument"
        self.add_argument(name, **kwargs)

    @checker.check_name_opt
    @checker.check_nargs_opt
    def add_opt(self, *name: str, **kwargs) -> None:
        '''Add optional argument.
        '''
        self.add_argument(*name, **kwargs)

    @checker.check_name_opt
    def add_opt_on(self, *name: str, **kwargs) -> None:
        '''Add boolean optional argument, default value is False.
        '''
        kwargs.update({"action": "store_true"})
        for key in ("type", "nargs", "const", "default", "choices"):
            assert key not in kwargs, f"'{key}' is an invalid argument"
        self.add_argument(*name, **kwargs)

    @checker.check_name_opt
    def add_opt_off(self, *name: str, **kwargs) -> None:
        '''Add boolean optional argument, default value is True.
        '''
        kwargs.update({"action": "store_false"})
        for key in ("type", "nargs", "const", "default", "choices"):
            assert key not in kwargs, f"'{key}' is an invalid argument"
        self.add_argument(*name, **kwargs)

    def add_subparsers(self, *args, **kwargs) -> _SubParsersAction:
        '''Add subparsers.
        '''
        # subparser: cannot have multiple subparser arguments
        kwargs.setdefault("title", "subcommands")
        kwargs.setdefault("description", None)
        kwargs.setdefault("dest", f"subcmd_{self.prog}")
        kwargs.setdefault("help", None)
        kwargs.setdefault("metavar", None)
        return ArgumentParser.add_subparsers(self, *args, **kwargs)

    def parse_args(  # pylint: disable=useless-parent-delegation
        self, args: Optional[Sequence[str]] = None,
        namespace: Optional[Namespace] = None
    ) -> Namespace:
        try:
            autocomplete(self)  # For tab completion
        except NameError:  # pragma: no cover
            pass  # pragma: no cover
        return super().parse_args(args, namespace)  # type: ignore

    def parse_known_args(  # pylint: disable=useless-parent-delegation
            self, args: Optional[Sequence[str]] = None,
            namespace: Optional[Namespace] = None
    ) -> Tuple[Namespace, List[str]]:
        return super().parse_known_args(args, namespace)  # type: ignore

    def __enable_help_action(self):  # pylint: disable=unused-private-member
        while len(self.__help_option) > 0:
            option, action = self.__help_option.popitem()
            self._option_string_actions[option] = action
        assert len(self.__help_option) == 0

    def __disable_help_action(self):  # pylint: disable=unused-private-member
        assert len(self.__help_option) == 0
        for option, action in self._option_string_actions.items():
            if isinstance(action, _HelpAction):
                self.__help_option[option] = action
        for option in self.__help_option:
            self._option_string_actions.pop(option)

    def preparse_from_sys_argv(self) -> Namespace:
        '''Preparse some arguments from sys.argv for tab completion.

        When arguments contain the help option, call parse_known_args()
        will print help message and exit. The command line can parse
        normally.

        But parameters added after calling preparse_from_sys_argv() will
        not show in the help message, because the exit occurred before
        adding parameters.

        So, disable the help action before calling parse_known_args().
        The help option will be stored, and restored after the call ends.
        '''

        def __dfs_enable_help_action(root: argp):
            root.__enable_help_action()  # pylint: disable=protected-access
            for _sub in root.next_parser:
                __dfs_enable_help_action(_sub)

        def __dfs_disable_help_action(root: argp):
            root.__disable_help_action()  # pylint: disable=protected-access
            for _sub in root.next_parser:
                __dfs_disable_help_action(_sub)

        try:
            __dfs_disable_help_action(self.root_parser)
            namespace, _ = self.root_parser.parse_known_args(self.argv)
            return namespace
        finally:
            __dfs_enable_help_action(self.root_parser)
