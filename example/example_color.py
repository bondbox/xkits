# coding:utf-8

from xkits import Style
from xkits import color


def example_background():
    print(f"{color.black_back('01234')} {color.lightblack_back('56789')}")
    print(f"{color.red_back('01234')} {color.lightred_back('56789')}")
    print(f"{color.green_back('01234')} {color.lightgreen_back('56789')}")
    print(f"{color.yellow_back('01234')} {color.lightyellow_back('56789')}")
    print(f"{color.blue_back('01234')} {color.lightblue_back('56789')}")
    print(f"{color.magenta_back('01234')} {color.lightmagenta_back('56789')}")
    print(f"{color.cyan_back('01234')} {color.lightcyan_back('56789')}")
    print(f"{color.white_back('01234')} {color.lightwhite_back('56789')}")


def example_foreground():
    print(f"{color.black('01234')} {color.lightblack('56789')}")
    print(f"{color.red('01234')} {color.lightred('56789')}")
    print(f"{color.green('01234')} {color.lightgreen('56789')}")
    print(f"{color.yellow('01234')} {color.lightyellow('56789')}")
    print(f"{color.blue('01234')} {color.lightblue('56789')}")
    print(f"{color.magenta('01234')} {color.lightmagenta('56789')}")
    print(f"{color.cyan('01234')} {color.lightcyan('56789')}")
    print(f"{color.white('01234')} {color.lightwhite('56789')}")


def example_style():
    print(f"bold:               0{color.bold('123456789')}0")
    print(f"normal:             0{color.normal('123456789')}0")
    print(f"dim:                0{color.dim('123456789')}0")
    print(f"italic:             0{color.italic('123456789')}0")
    print(f"underline:          0{color.underline('123456789')}0")
    print(f"slow_blink:         0{color.slow_blink('123456789')}0")
    print(f"rapid_blink:        0{color.rapid_blink('123456789')}0")
    print(f"invert:             0{color.invert('123456789')}0")
    print(f"hide:               0{color.hide('123456789')}0")
    print(f"strikethrough:      0{color.strikethrough('123456789')}0")
    print(f"doubly_underlined:  0{color.doubly_underlined('123456789')}0")
    print(f"reveal:             0{color.reveal('123456789')}0")


if __name__ == "__main__":
    example_background()
    example_foreground()
    example_style()

    segment1 = color.red("123").add_style(Style.UNDERLINE)
    segment2 = color.green(456).add_style(Style.STRIKETHROUGH)
    segment3 = color.yellow(789).add_style(Style.DOUBLYUNDERLINED)
    print(f"COLORFUL:  {color.invert(f'0{segment1}{segment2}')}{segment3}0")
