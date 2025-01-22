xkits
=====

Python toolkit.

Language
--------

- **[简体中文](docs/zh/README.md)**

Features
--------

- **Quickly create command line programs based on `Python`**
- **Built in logger module and management options**
- **Manage completion via [xargcomplete](docs/xargcomplete.md)**

Requires
--------

- `Python` >= 3.8

Build
-----

Fast build and install via [xpip](https://github.com/bondbox/xpip):

```shell
xpip-build setup --clean --all --install
```

or build via shell:

```shell
rm -rf "build" "dist" "*.egg-info"
python setup.py check sdist bdist_wheel --universal
```
