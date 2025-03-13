# coding:utf-8

import os
from typing import Optional
from typing import Sequence

from .actuator import add_command
from .actuator import commands
from .actuator import run_command
from .attribute import __author__
from .attribute import __author_email__
from .attribute import __prog_name__
from .attribute import __prog_project__
from .attribute import __project__
from .attribute import __urlhome__
from .attribute import __version__
from .parser import argp


class project:

    def __init__(self, name: str, license: str, allow_update: bool = False):  # pylint: disable=redefined-builtin # noqa:E501
        # check illegal characters in project name
        for char in [" "]:
            if char in name:
                raise ValueError(f"Illegal character '{char}' in '{name}'")
        folder: str = name.replace("-", "_")
        self.__name: str = name
        self.__folder: str = folder
        self.__license: str = license
        self.__allow_update: bool = allow_update

    @property
    def name(self) -> str:
        return self.__name

    @property
    def folder(self) -> str:
        return self.__folder

    @property
    def license(self) -> str:
        return self.__license

    @property
    def allow_update(self) -> bool:
        return self.__allow_update

    def write(self, path: str, content: str) -> bool:
        if not os.path.exists(path) or self.allow_update:
            with open(path, "w", encoding="utf-8") as whdl:
                if len(content) > 0 and content[-1] != "\n":
                    content += "\n"
                whdl.write(content)
        return True

    def init_requirements(self):
        self.write("requirements.txt", f'''{__project__} >= {__version__}''')

    def init_coveragerc(self):
        self.write(".coveragerc", f'''[run]
omit =
    {self.folder}/unittest/*
    {self.folder}/attribute.py

[report]
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if __name__ == .__main__.:
    def __repr__
''')

    def init_pylintrc(self):
        self.write(".pylintrc", '''[MASTER]
disable=
    C0103,   # invalid-name
    C0114,   # missing-module-docstring
    C0115,   # missing-class-docstring
    C0116,   # missing-function-docstring
    C0301,   # line-too-long
''')

    def init_makefile(self):
        self.write("Makefile", f'''MAKEFLAGS += --always-make

all: build reinstall test


clean-cover:
	rm -rf cover .coverage coverage.xml htmlcov
clean-tox:
	rm -rf .stestr .tox
clean: build-clean test-clean clean-cover clean-tox


upload:
	xpip-upload --config-file .pypirc dist/*


build-clean:
	xpip-build --debug setup --clean
build-requirements:
	pip3 install -r requirements.txt
build: build-clean build-requirements
	xpip-build --debug setup --all


install:
	pip3 install --force-reinstall --no-deps dist/*.whl
uninstall:
	pip3 uninstall -y {self.name}
reinstall: uninstall install


test-prepare:
	pip3 install --upgrade mock pylint flake8 pytest pytest-cov
pylint:
	pylint $(shell git ls-files {self.folder}/*.py test/*.py example/*.py)
flake8:
	flake8 {self.folder} --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 {self.folder} --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
pytest:
	pytest --cov={self.folder} --cov-report=term-missing --cov-report=xml --cov-report=html --cov-config=.coveragerc --cov-fail-under=100
pytest-clean:
	rm -rf .pytest_cache
test: test-prepare pylint flake8 pytest
test-clean: pytest-clean
''')  # noqa:W191,E101,E501

    def init_project(self):
        os.makedirs(self.folder, exist_ok=True)
        os.makedirs(os.path.join(self.folder, "unittest"), exist_ok=True)
        self.write(os.path.join(self.folder, "__init__.py"), "")
        self.write(os.path.join(self.folder, "unittest", "__init__.py"), "")
        self.write(os.path.join(self.folder, "attribute.py"),
                   f'''# coding:utf-8

from urllib.parse import urljoin

__project__ = "{self.name}"
__version__ = "0.1.alpha.1"
__description__ = "Automatically created by {__prog_project__}."
__urlhome__ = "{__urlhome__}"
__urlcode__ = __urlhome__
__urldocs__ = __urlhome__
__urlbugs__ = urljoin(__urlhome__, "issues")

# author
__author__ = "{__author__}"
__author_email__ = "{__author_email__}"
''')
        self.write(os.path.join(self.folder, "command.py"),
                   f'''# coding:utf-8

from typing import Optional
from typing import Sequence

from {__prog_name__} import add_command
from {__prog_name__} import argp
from {__prog_name__} import commands
from {__prog_name__} import run_command

from {self.folder}.attribute import __description__
from {self.folder}.attribute import __project__
from {self.folder}.attribute import __urlhome__
from {self.folder}.attribute import __version__


@add_command(__project__, description=__description__)
def add_cmd(_arg: argp):
    pass


@run_command(add_cmd)
def run_cmd(cmds: commands) -> int:
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {{__urlhome__}}.")  # noqa:E501
''')

    def init_readme(self):
        self.write("README.md", f'''# {self.name}

> Automatically created by {__prog_project__}.''')

    def init_setup(self):
        # create setup.cfg
        self.write("setup.cfg", f'''[metadata]
keywords = command-line, argparse, argcomplete
long_description = file: README.md
long_description_content_type = text/markdown
license = {self.license}
license_files = LICENSE
platforms = any
classifiers =
    Programming Language :: Python
    Programming Language :: Python :: 3

[options]
zip_safe = True
include_package_data = True
python_requires = >=3.8

[options.entry_points]
console_scripts =
    {self.name} = {self.folder}.command:main
''')

        # create setup.py
        self.write("setup.py", f'''# coding=utf-8

from setuptools import find_packages
from setuptools import setup

from {self.folder}.attribute import __author__
from {self.folder}.attribute import __author_email__
from {self.folder}.attribute import __description__
from {self.folder}.attribute import __project__
from {self.folder}.attribute import __urlbugs__
from {self.folder}.attribute import __urlcode__
from {self.folder}.attribute import __urldocs__
from {self.folder}.attribute import __urlhome__
from {self.folder}.attribute import __version__


def all_requirements():
    def read_requirements(path: str):
        with open(path, "r", encoding="utf-8") as rhdl:
            return rhdl.read().splitlines()

    requirements = read_requirements("requirements.txt")
    return requirements


setup(
    name=__project__,
    version=__version__,
    description=__description__,
    url=__urlhome__,
    author=__author__,
    author_email=__author_email__,
    project_urls={{"Source Code": __urlcode__,
                  "Bug Tracker": __urlbugs__,
                  "Documentation": __urldocs__}},
    packages=find_packages(include=["{self.folder}*"], exclude=["{self.folder}.unittest"]),
    install_requires=all_requirements())
''')  # noqa:E501

    def create(self) -> int:
        self.init_requirements()
        self.init_coveragerc()
        self.init_pylintrc()
        self.init_makefile()
        self.init_project()
        self.init_readme()
        self.init_setup()
        return 0


@add_command("init", help="Initialize a command-line project.")
def add_cmd_init(_arg: argp):
    _arg.add_opt_on("--update", help="allow updating existing files")
    _arg.add_argument("--license", type=str, nargs=1, metavar="LICENSE",
                      default=["MIT"], help="select license, default to MIT")
    _arg.add_pos("project_name", type=str, metavar="PROJECT")


@run_command(add_cmd_init)
def run_cmd_init(cmds: commands) -> int:
    return project(name=cmds.args.project_name,
                   license=cmds.args.license[0],
                   allow_update=cmds.args.update
                   ).create()


@add_command(__prog_project__, description="Create a command-line project.")
def add_cmd(_arg: argp):
    pass


@run_command(add_cmd, add_cmd_init)
def run_cmd(cmds: commands) -> int:  # pylint: disable=unused-argument
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {__urlhome__}.")  # noqa:E501
