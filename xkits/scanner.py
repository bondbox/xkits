# coding:utf-8

from hashlib import md5
from hashlib import sha1
from hashlib import sha256
import os
from queue import Empty
from queue import Queue
import stat
from threading import Thread
from threading import current_thread  # noqa:H306
from typing import Callable
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set

from .actuator import commands

CPU_COUNT = os.cpu_count()
THDNUM_MINIMUM = 1
THDNUM_MAXIMUM = CPU_COUNT if isinstance(CPU_COUNT, int) else 64
THDNUM_DEFAULT = int(THDNUM_MAXIMUM / 2)


class scanner:
    '''scan objects
    '''

    class object:  # pylint: disable=too-many-public-methods

        def __init__(self, path: str):
            assert isinstance(path, str)
            self.__path = os.path.normpath(path)
            self.__abspath = os.path.abspath(self.__path)
            self.__realpath = os.path.realpath(self.__abspath)

        @property
        def path(self) -> str:
            return self.__path

        @property
        def abspath(self) -> str:
            return self.__abspath

        @property
        def realpath(self) -> str:
            return self.__realpath

        @property
        def stat(self) -> os.stat_result:
            return os.stat(self.abspath)

        @property
        def lstat(self) -> os.stat_result:
            return os.lstat(self.abspath)

        @property
        def uid(self) -> int:
            '''user id of owner
            '''
            return self.stat.st_uid

        @property
        def gid(self) -> int:
            '''group id of owner
            '''
            return self.stat.st_gid

        @property
        def mode(self) -> int:
            return self.stat.st_mode

        @property
        def ctime(self) -> float:
            return self.stat.st_ctime

        @property
        def atime(self) -> float:
            '''time of most recent access
            '''
            return self.stat.st_atime

        @property
        def mtime(self) -> float:
            '''time of most recent content modification
            '''
            return self.stat.st_mtime

        @property
        def size(self) -> int:
            return self.stat.st_size

        @property
        def isdir(self) -> bool:
            return stat.S_ISDIR(self.stat.st_mode)

        @property
        def isreg(self) -> bool:
            return stat.S_ISREG(self.stat.st_mode)

        @property
        def isfile(self) -> bool:
            return self.isreg

        @property
        def islink(self) -> bool:
            return stat.S_ISLNK(self.lstat.st_mode)

        @property
        def issym(self) -> bool:
            return self.islink

        def hash(self, *args, size=1024**2) -> Generator[str, None, None]:
            assert self.isfile and not self.issym
            with open(self.abspath, "rb") as fhandler:
                while True:
                    data = fhandler.read(size)
                    if not data:
                        break
                    for obj in args:
                        obj.update(data)
            return (obj.hexdigest() for obj in args)

        @property
        def md5(self) -> str:
            code, = self.hash(md5())
            return code

        @property
        def sha1(self) -> str:
            code, = self.hash(sha1())
            return code

        @property
        def sha256(self) -> str:
            code, = self.hash(sha256())
            return code

    def __init__(self):
        self.__objdict: Dict[str, scanner.object] = {}
        self.__objects: Set[scanner.object] = set()
        self.__objsyms: Set[scanner.object] = set()
        self.__objregs: Set[scanner.object] = set()
        self.__objdirs: Set[scanner.object] = set()

    def __iter__(self):
        return iter(self.__objects)

    def __getitem__(self, key: str):
        return self.__objdict[key]

    @property
    def dirs(self) -> Set[object]:
        return self.__objdirs

    @property
    def files(self) -> Set[object]:
        return self.__objregs

    @property
    def links(self) -> Set[object]:
        return self.__objsyms

    def add(self, obj: object):
        assert isinstance(obj, scanner.object)
        if obj.path not in self.__objdict:
            self.__objdict[obj.path] = obj
            self.__objects.add(obj)
            if obj.issym:
                self.__objsyms.add(obj)
            if obj.isdir:
                self.__objdirs.add(obj)
            elif obj.isreg:
                self.__objregs.add(obj)

    @classmethod
    def load(cls,  # pylint: disable=R0913,R0914,R0915,R0917
             paths: Sequence[str],
             exclude: Optional[Sequence[str]] = None,
             linkdir: bool = True,
             threads: int = THDNUM_DEFAULT,
             handler: Optional[Callable[[object], bool]] = None):
        if exclude is None:
            exclude = []

        assert isinstance(paths, Sequence)
        assert isinstance(exclude, Sequence)
        assert isinstance(linkdir, bool)
        assert isinstance(threads, int)

        cmds = commands()
        thds = min(max(THDNUM_MINIMUM, threads), THDNUM_MAXIMUM)

        def rpath(path: str) -> str:
            assert isinstance(path, str)
            return os.path.relpath(path)

        # filter files and directorys
        def path_filter() -> Set[str]:
            filter_paths: Set[str] = set()

            for path in exclude:
                filter_paths.add(rpath(path))

            return filter_paths

        class task_stat:  # pylint: disable=too-few-public-methods

            def __init__(self):
                self.exit = False
                self.handler = handler
                self.scanner = scanner()
                self.filter: Set[str] = path_filter()
                self.q_path: "Queue[str]" = Queue()
                self.q_task: "Queue[scanner.object]" = Queue(maxsize=thds * 2)

        scan_stat = task_stat()

        def task_scan_path():
            scanned_dirs = set()
            name = current_thread().name
            cmds.logger.debug("task thread[%s] start", name)
            while not scan_stat.exit or not scan_stat.q_path.empty():
                try:
                    path = scan_stat.q_path.get(timeout=0.01)
                except Empty:
                    continue

                path = rpath(path)
                assert isinstance(path, str)

                if path in scan_stat.filter or not os.path.exists(path):
                    cmds.logger.debug("scan filter %s", path)
                    scan_stat.q_path.task_done()
                    continue

                if os.path.isdir(path) and path not in scanned_dirs:
                    scanned_dirs.add(path)
                    # scan symbolic link dirs?
                    if not os.path.islink(path) or linkdir:
                        for sub in os.listdir(path=path):
                            spath = os.path.join(path, sub)
                            scan_stat.q_path.put(spath)

                ret = True
                obj = scanner.object(path)

                if isinstance(scan_stat.handler, Callable):
                    ret = scan_stat.handler(obj)
                    assert isinstance(ret, bool)

                if ret is True:
                    scan_stat.q_task.put(obj)
                scan_stat.q_path.task_done()
            cmds.logger.debug("task thread[%s] exit", name)

        def task_scan():
            name = current_thread().name
            cmds.logger.debug("task thread[%s] start", name)
            while not scan_stat.exit or not scan_stat.q_task.empty():
                try:
                    obj = scan_stat.q_task.get(timeout=0.01)
                except Empty:
                    continue

                cmds.logger.debug("scan %s", obj.path)
                scan_stat.scanner.add(obj=obj)
                scan_stat.q_task.task_done()
            cmds.logger.debug("task thread[%s] exit", name)

        task_threads: List[Thread] = []
        task_threads.append(Thread(target=task_scan, name="xkits-scan"))
        task_threads.extend([
            Thread(target=task_scan_path, name=f"xkits-scan{i}")
            for i in range(thds)
        ])

        for thread in task_threads:
            thread.start()

        for path in paths:
            scan_stat.q_path.put(path)

        scan_stat.q_path.join()
        scan_stat.q_task.join()
        scan_stat.exit = True

        for thread in task_threads:
            thread.join()

        return scan_stat.scanner
