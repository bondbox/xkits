# coding:utf-8

import os

from psutil import Process


def memory_info(process: Process):
    memory_info = process.memory_info()
    print(f"VMS (Virtual Memory Size)\t{memory_info.vms / 1024 / 1024:.2f} MB\t{memory_info.vms}")  # noqa:E501
    print(f"RSS (Resident Set Size)  \t{memory_info.rss / 1024 / 1024:.2f} MB\t{memory_info.rss}")  # noqa:E501


def main():
    pid: int = os.getpid()
    print(f"Hello, PID {pid}")
    process: Process = Process(pid)
    print("Before import:")
    memory_info(process)
    import xkits  # noqa:F401
    print("After import:")
    memory_info(process)
    print("Goodbye!")


if __name__ == "__main__":
    main()
