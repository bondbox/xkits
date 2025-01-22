# coding:utf-8

import unittest

from xkits import Back
from xkits import Fore
from xkits import Style
from xkits import color
from xkits import commands


class test_safile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_reset(self):
        self.assertEqual(str(color.reset()), Style.RESET_ALL)

    def test_add_style(self):
        text1 = color("unittest style")
        text2 = color("unittest style")
        text1.add_style(Style.BRIGHT)
        text1.add_style(Style.UNDERLINE)
        text2.style = {Style.BRIGHT, Style.UNDERLINE}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(text1.style, text2.style)

    def test_bold_style(self):
        text1 = color("unittest bold")
        text2 = color.bold(text1)
        text1.style = {Style.BRIGHT}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_dim_style(self):
        text1 = color("unittest dim")
        text2 = color.dim(text1)
        text1.style = {Style.DIM}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_normal_style(self):
        text1 = color("unittest normal")
        text2 = color.normal(text1)
        text1.style = {Style.NORMAL}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_italic_style(self):
        text1 = color("unittest italic")
        text2 = color.italic(text1)
        text1.style = {Style.ITALIC}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_underline_style(self):
        text1 = color("unittest underline")
        text2 = color.underline(text1)
        text1.style = {Style.UNDERLINE}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_slow_blink_style(self):
        text1 = color("unittest slow_blink")
        text2 = color.slow_blink(text1)
        text1.style = {Style.SLOWBLINK}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_rapid_blink_style(self):
        text1 = color("unittest rapid_blink")
        text2 = color.rapid_blink(text1)
        text1.style = {Style.RAPIDBLINK}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_invert_style(self):
        text1 = color("unittest invert")
        text2 = color.invert(text1)
        text1.style = {Style.INVERT}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_hide_style(self):
        text1 = color("unittest hide")
        text2 = color.hide(text1)
        text1.style = {Style.HIDE}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_strikethrough_style(self):
        text1 = color("unittest strikethrough")
        text2 = color.strikethrough(text1)
        text1.style = {Style.STRIKETHROUGH}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_doubly_underlined_style(self):
        text1 = color("unittest doubly_underlined")
        text2 = color.doubly_underlined(text1)
        text1.style = {Style.DOUBLYUNDERLINED}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_reveal_style(self):
        text1 = color("unittest reveal")
        text2 = color.reveal(text1)
        text1.style = {Style.REVEAL}
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_black_foreground(self):
        text1 = color("unittest black")
        text2 = color.black(text1)
        text1.foreground = Fore.BLACK
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_red_foreground(self):
        text1 = color("unittest red")
        text2 = color.red(text1)
        text1.foreground = Fore.RED
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_green_foreground(self):
        text1 = color("unittest green")
        text2 = color.green(text1)
        text1.foreground = Fore.GREEN
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_yellow_foreground(self):
        text1 = color("unittest yellow")
        text2 = color.yellow(text1)
        text1.foreground = Fore.YELLOW
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_blue_foreground(self):
        text1 = color("unittest blue")
        text2 = color.blue(text1)
        text1.foreground = Fore.BLUE
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_magenta_foreground(self):
        text1 = color("unittest magenta")
        text2 = color.magenta(text1)
        text1.foreground = Fore.MAGENTA
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_cyan_foreground(self):
        text1 = color("unittest cyan")
        text2 = color.cyan(text1)
        text1.foreground = Fore.CYAN
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_white_foreground(self):
        text1 = color("unittest white")
        text2 = color.white(text1)
        text1.foreground = Fore.WHITE
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightblack_foreground(self):
        text1 = color("unittest lightblack")
        text2 = color.lightblack(text1)
        text1.foreground = Fore.LIGHTBLACK_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightred_foreground(self):
        text1 = color("unittest lightred")
        text2 = color.lightred(text1)
        text1.foreground = Fore.LIGHTRED_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightgreen_foreground(self):
        text1 = color("unittest lightgreen")
        text2 = color.lightgreen(text1)
        text1.foreground = Fore.LIGHTGREEN_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightyellow_foreground(self):
        text1 = color("unittest lightyellow")
        text2 = color.lightyellow(text1)
        text1.foreground = Fore.LIGHTYELLOW_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightblue_foreground(self):
        text1 = color("unittest lightblue")
        text2 = color.lightblue(text1)
        text1.foreground = Fore.LIGHTBLUE_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightmagenta_foreground(self):
        text1 = color("unittest lightmagenta")
        text2 = color.lightmagenta(text1)
        text1.foreground = Fore.LIGHTMAGENTA_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightcyan_foreground(self):
        text1 = color("unittest lightcyan")
        text2 = color.lightcyan(text1)
        text1.foreground = Fore.LIGHTCYAN_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightwhite_foreground(self):
        text1 = color("unittest lightwhite")
        text2 = color.lightwhite(text1)
        text1.foreground = Fore.LIGHTWHITE_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_black_background(self):
        text1 = color("unittest black")
        text2 = color.black_back(text1)
        text1.background = Back.BLACK
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_red_background(self):
        text1 = color("unittest red")
        text2 = color.red_back(text1)
        text1.background = Back.RED
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_green_background(self):
        text1 = color("unittest green")
        text2 = color.green_back(text1)
        text1.background = Back.GREEN
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_yellow_background(self):
        text1 = color("unittest yellow")
        text2 = color.yellow_back(text1)
        text1.background = Back.YELLOW
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_blue_background(self):
        text1 = color("unittest blue")
        text2 = color.blue_back(text1)
        text1.background = Back.BLUE
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_magenta_background(self):
        text1 = color("unittest magenta")
        text2 = color.magenta_back(text1)
        text1.background = Back.MAGENTA
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_cyan_background(self):
        text1 = color("unittest cyan")
        text2 = color.cyan_back(text1)
        text1.background = Back.CYAN
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_white_background(self):
        text1 = color("unittest white")
        text2 = color.white_back(text1)
        text1.background = Back.WHITE
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightblack_background(self):
        text1 = color("unittest lightblack")
        text2 = color.lightblack_back(text1)
        text1.background = Back.LIGHTBLACK_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightred_background(self):
        text1 = color("unittest lightred")
        text2 = color.lightred_back(text1)
        text1.background = Back.LIGHTRED_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightgreen_background(self):
        text1 = color("unittest lightgreen")
        text2 = color.lightgreen_back(text1)
        text1.background = Back.LIGHTGREEN_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightyellow_background(self):
        text1 = color("unittest lightyellow")
        text2 = color.lightyellow_back(text1)
        text1.background = Back.LIGHTYELLOW_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightblue_background(self):
        text1 = color("unittest lightblue")
        text2 = color.lightblue_back(text1)
        text1.background = Back.LIGHTBLUE_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightmagenta_background(self):
        text1 = color("unittest lightmagenta")
        text2 = color.lightmagenta_back(text1)
        text1.background = Back.LIGHTMAGENTA_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightcyan_background(self):
        text1 = color("unittest lightcyan")
        text2 = color.lightcyan_back(text1)
        text1.background = Back.LIGHTCYAN_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))

    def test_lightwhite_background(self):
        text1 = color("unittest lightwhite")
        text2 = color.lightwhite_back(text1)
        text1.background = Back.LIGHTWHITE_EX
        commands().stdout(f"text1: {text1}")
        commands().stdout(f"text2: {text2}")
        self.assertEqual(str(text1), str(text2))


if __name__ == "__main__":
    unittest.main()
