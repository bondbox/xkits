xkits
=====

Python 工具包。

特性
----

- **快速创建基于 `Python` 的命令行程序**
- **提供内建的 `logger` 模块和管理选项**
- **通过 [xargcomplete](xargcomplete.md) 管理命令补全**

要求
----

- Python >= 3.8

构建
----

通过 [xpip](https://github.com/bondbox/xpip) 工具可快速构建和安装：

```shell
xpip-build setup --clean --all --install
```

或者通过 `shell` 命令构建:

```shell
rm -rf "build" "dist" "*.egg-info"
python setup.py check sdist bdist_wheel --universal
```
