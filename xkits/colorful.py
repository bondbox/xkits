# coding:utf-8

from typing import Optional
from typing import Set
from typing import Union

from colorama import Back
from colorama import Fore
from colorama.ansi import AnsiStyle
from colorama.ansi import code_to_chars


class AnsiXStyle(AnsiStyle):  # pylint: disable=too-few-public-methods
    ITALIC = 3
    UNDERLINE = 4
    SLOWBLINK = 5
    RAPIDBLINK = 6
    INVERT = 7
    HIDE = 8
    STRIKETHROUGH = 9
    DOUBLYUNDERLINED = 21
    RESET_ITALIC = 23
    RESET_UNDERLINE = 24
    RESET_BLINK = 25
    RESET_INVERT = 27
    REVEAL = 28
    RESET_STRIKETHROUGH = 29


Style = AnsiXStyle()
StyleType = Union[str, int]
SytleReset = {
    Style.BRIGHT: Style.NORMAL,
    Style.DIM: Style.NORMAL,
    Style.ITALIC: Style.RESET_ITALIC,
    Style.UNDERLINE: Style.RESET_UNDERLINE,
    Style.SLOWBLINK: Style.RESET_BLINK,
    Style.RAPIDBLINK: Style.RESET_BLINK,
    Style.INVERT: Style.RESET_INVERT,
    Style.STRIKETHROUGH: Style.RESET_STRIKETHROUGH,
    Style.DOUBLYUNDERLINED: Style.RESET_UNDERLINE,
}


class color(str):  # pylint: disable=too-many-public-methods
    '''Colorful terminal text

    Reference: https://en.wikipedia.org/wiki/ANSI_escape_code
    '''

    def __init__(self, obj: object):  # pylint: disable=unused-argument
        self.__background: Optional[str] = None
        self.__foreground: Optional[str] = None
        self.__style: Set[str] = set()
        super().__init__()

    def __str__(self) -> str:
        message: str = super().__str__()

        if isinstance(self.foreground, str):
            message = f"{self.foreground}{message}{Fore.RESET}"

        if isinstance(self.background, str):
            message = f"{self.background}{message}{Back.RESET}"

        if len(self.style) > 0:
            for style in self.style:
                reset_style = SytleReset.get(style, Style.RESET_ALL)
                message = f"{style}{message}{reset_style}"
        return message

    @property
    def background(self) -> Optional[str]:
        return self.__background

    @background.setter
    def background(self, value: str):
        assert isinstance(value, str), f"Unexpected type: {type(value)}"
        self.__background = value

    @property
    def foreground(self) -> Optional[str]:
        return self.__foreground

    @foreground.setter
    def foreground(self, value: str):
        assert isinstance(value, str), f"Unexpected type: {type(value)}"
        self.__foreground = value

    @property
    def style(self) -> Set[str]:
        return self.__style

    @style.setter
    def style(self, value: Set[StyleType]):
        assert isinstance(value, set), f"Unexpected type: {type(value)}"
        _value: Set[str] = {code_to_chars(v) if isinstance(v, int) else v
                            for v in value}
        self.__style = _value

    def add_style(self, value: StyleType) -> "color":
        assert isinstance(value, (str, int)), f"Unexpected type: {type(value)}"
        _value: str = code_to_chars(value) if isinstance(value, int) else value
        self.__style.add(_value)
        return self

    @classmethod
    def new_background(cls, obj: object, value: str) -> "color":
        colour: color = color(obj)
        colour.background = value
        return colour

    @classmethod
    def new_foreground(cls, obj: object, value: str) -> "color":
        colour: color = color(obj)
        colour.foreground = value
        return colour

    @classmethod
    def new_style(cls, obj: object, value: Set[StyleType]) -> "color":
        colour: color = color(obj)
        colour.style = value
        return colour

    @classmethod
    def reset(cls) -> str:
        return Style.RESET_ALL

    @classmethod
    def bold(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.BRIGHT})

    @classmethod
    def dim(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.DIM})

    @classmethod
    def italic(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.ITALIC})

    @classmethod
    def underline(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.UNDERLINE})

    @classmethod
    def slow_blink(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.SLOWBLINK})

    @classmethod
    def rapid_blink(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.RAPIDBLINK})

    @classmethod
    def invert(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.INVERT})

    @classmethod
    def hide(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.HIDE})

    @classmethod
    def strikethrough(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.STRIKETHROUGH})

    @classmethod
    def doubly_underlined(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.DOUBLYUNDERLINED})

    @classmethod
    def normal(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.NORMAL})

    @classmethod
    def reveal(cls, obj: object) -> "color":
        return color.new_style(obj, {Style.REVEAL})

    @classmethod
    def black(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.BLACK)

    @classmethod
    def red(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.RED)

    @classmethod
    def green(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.GREEN)

    @classmethod
    def yellow(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.YELLOW)

    @classmethod
    def blue(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.BLUE)

    @classmethod
    def magenta(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.MAGENTA)

    @classmethod
    def cyan(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.CYAN)

    @classmethod
    def white(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.WHITE)

    @classmethod
    def lightblack(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.LIGHTBLACK_EX)

    @classmethod
    def lightred(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.LIGHTRED_EX)

    @classmethod
    def lightgreen(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.LIGHTGREEN_EX)

    @classmethod
    def lightyellow(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.LIGHTYELLOW_EX)

    @classmethod
    def lightblue(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.LIGHTBLUE_EX)

    @classmethod
    def lightmagenta(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.LIGHTMAGENTA_EX)

    @classmethod
    def lightcyan(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.LIGHTCYAN_EX)

    @classmethod
    def lightwhite(cls, obj: object) -> "color":
        return color.new_foreground(obj, Fore.LIGHTWHITE_EX)

    @classmethod
    def black_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.BLACK)

    @classmethod
    def red_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.RED)

    @classmethod
    def green_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.GREEN)

    @classmethod
    def yellow_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.YELLOW)

    @classmethod
    def blue_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.BLUE)

    @classmethod
    def magenta_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.MAGENTA)

    @classmethod
    def cyan_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.CYAN)

    @classmethod
    def white_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.WHITE)

    @classmethod
    def lightblack_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.LIGHTBLACK_EX)

    @classmethod
    def lightred_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.LIGHTRED_EX)

    @classmethod
    def lightgreen_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.LIGHTGREEN_EX)

    @classmethod
    def lightyellow_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.LIGHTYELLOW_EX)

    @classmethod
    def lightblue_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.LIGHTBLUE_EX)

    @classmethod
    def lightmagenta_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.LIGHTMAGENTA_EX)

    @classmethod
    def lightcyan_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.LIGHTCYAN_EX)

    @classmethod
    def lightwhite_back(cls, obj: object) -> "color":
        return color.new_background(obj, Back.LIGHTWHITE_EX)
