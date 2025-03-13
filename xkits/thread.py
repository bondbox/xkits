# coding:utf-8

from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import sys
from threading import Lock
from threading import Thread
from threading import current_thread  # noqa:H306
from time import time
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generic
from typing import Iterator
from typing import Optional
from typing import Set
from typing import Tuple
from typing import TypeVar

from .actuator import Logger
from .actuator import commands  # noqa:H306

LKIT = TypeVar("LKIT")
LKNT = TypeVar("LKNT")


class NamedLock(Generic[LKNT]):

    class LockItem(Generic[LKIT]):
        def __init__(self, name: LKIT):
            self.__lock: Lock = Lock()
            self.__name: LKIT = name

        @property
        def name(self) -> LKIT:
            return self.__name

        @property
        def lock(self) -> Lock:
            return self.__lock

    def __init__(self):
        self.__locks: Dict[LKNT, NamedLock.LockItem[LKNT]] = {}
        self.__inter: Lock = Lock()  # internal lock

    def __len__(self) -> int:
        return len(self.__locks)

    def __iter__(self) -> Iterator[LockItem[LKNT]]:
        return iter(self.__locks.values())

    def __contains__(self, name: LKNT) -> bool:
        return name in self.__locks

    def __getitem__(self, name: LKNT) -> Lock:
        return self.lookup(name).lock

    def lookup(self, name: LKNT) -> LockItem[LKNT]:
        try:
            return self.__locks[name]
        except KeyError:
            with self.__inter:
                if name not in self.__locks:
                    lock = self.LockItem(name)
                    self.__locks.setdefault(name, lock)
                    assert self.__locks[name] is lock
                    return lock

                lock = self.__locks[name]  # pragma: no cover
                assert lock.name == name  # pragma: no cover
                return lock  # pragma: no cover


class ThreadPool(ThreadPoolExecutor):
    '''Thread Pool'''

    def __init__(self, max_workers: Optional[int] = None,
                 thread_name_prefix: str = "work_thread",
                 initializer: Optional[Callable] = None,
                 initargs: Tuple = ()):
        '''Initializes an instance based on ThreadPoolExecutor.'''
        self.__cmds: commands = commands()
        if isinstance(max_workers, int):
            max_workers = max(max_workers, 2)
        super().__init__(max_workers, thread_name_prefix, initializer, initargs)  # noqa:E501

    @property
    def cmds(self) -> commands:
        '''command-line toolkit'''
        return self.__cmds

    @property
    def alive_threads(self) -> Set[Thread]:
        '''alive threads'''
        return {thread for thread in self._threads if thread.is_alive()}

    @property
    def other_threads(self) -> Set[Thread]:
        '''other threads'''
        current: Thread = current_thread()
        return {thread for thread in self._threads if thread is not current}

    @property
    def other_alive_threads(self) -> Set[Thread]:
        '''other alive threads'''
        return {thread for thread in self.other_threads if thread.is_alive()}


class TaskJob():  # pylint: disable=too-many-instance-attributes
    '''Task Job'''

    def __init__(self, no: int, fn: Callable, *args: Any, **kwargs: Any):
        self.__no: int = no
        self.__fn: Callable = fn
        self.__args: Tuple[Any, ...] = args
        self.__kwargs: Dict[str, Any] = kwargs
        self.__result: Any = LookupError(f"Job{no} is not started")
        self.__created: float = time()
        self.__started: float = 0.0
        self.__stopped: float = 0.0

    def __str__(self) -> str:
        args = list(self.args) + list(f"{k}={v}" for k, v in self.kwargs)
        info: str = ", ".join(f"{a}" for a in args)
        return f"Job{self.id} {self.fn}({info})"

    @property
    def id(self) -> int:
        '''job id'''
        return self.__no

    @property
    def fn(self) -> Callable:
        '''job callable function'''
        return self.__fn

    @property
    def args(self) -> Tuple[Any, ...]:
        '''job callable arguments'''
        return self.__args

    @property
    def kwargs(self) -> Dict[str, Any]:
        '''job callable keyword arguments'''
        return self.__kwargs

    @property
    def result(self) -> Any:
        '''job callable function return value'''
        if isinstance(self.__result, Exception):
            raise self.__result
        return self.__result

    @property
    def created(self) -> float:
        '''job created time'''
        return self.__created

    @property
    def started(self) -> float:
        '''job started time'''
        return self.__started

    @property
    def stopped(self) -> float:
        '''job stopped time'''
        return self.__stopped

    def run(self) -> bool:
        '''run job'''
        try:
            if self.__started > 0.0:
                raise RuntimeError(f"{self} is already started")
            self.__started = time()
            self.__result = self.fn(*self.args, **self.kwargs)
            return True
        except Exception as error:  # pylint: disable=broad-exception-caught
            self.__result = error
            return False
        finally:
            self.__stopped = time()


if sys.version_info >= (3, 9):
    JobQueue = Queue[Optional[TaskJob]]  # noqa: E501, pragma: no cover, pylint: disable=unsubscriptable-object
else:  # Python3.8 TypeError
    JobQueue = Queue  # pragma: no cover


class TaskPool(Dict[int, TaskJob]):  # noqa: E501, pylint: disable=too-many-instance-attributes
    '''Task Thread Pool'''

    def __init__(self, workers: int = 1, jobs: int = 0, prefix: str = "task"):
        wsize: int = max(workers, 1)
        qsize = max(wsize, jobs) if jobs > 0 else jobs
        self.__cmds: commands = commands()
        self.__jobs: JobQueue = Queue(qsize)
        self.__prefix: str = prefix or "task"
        self.__threads: Set[Thread] = set()
        self.__intlock: Lock = Lock()  # internal lock
        self.__running: bool = False
        self.__workers: int = wsize
        self.__counter: int = 0
        self.__suceess: int = 0
        self.__failure: int = 0
        super().__init__()

    def __enter__(self):
        self.startup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    @property
    def jobs(self) -> JobQueue:
        '''task jobs'''
        return self.__jobs

    @property
    def cmds(self) -> commands:
        '''command-line toolkit'''
        return self.__cmds

    @property
    def thread_name_prefix(self) -> str:
        '''task thread name prefix'''
        return self.__prefix

    @property
    def threads(self) -> Set[Thread]:
        '''task threads'''
        return self.__threads

    @property
    def running(self) -> bool:
        '''task threads are started'''
        return self.__running

    @property
    def workers(self) -> int:
        '''task workers'''
        return self.__workers

    @property
    def counter(self) -> int:
        '''task job counter'''
        return self.__counter

    @property
    def suceess(self) -> int:
        '''suceess job counter'''
        return self.__suceess

    @property
    def failure(self) -> int:
        '''suceess job counter'''
        return self.__failure

    def task(self):
        '''execute a task from jobs queue'''
        counter: int = 0
        suceess: int = 0
        failure: int = 0
        logger: Logger = self.cmds.logger
        logger.debug("Task thread %s is running", current_thread().name)
        while True:
            job: Optional[TaskJob] = self.jobs.get(block=True)
            if job is None:  # stop task
                self.jobs.put(job)  # notice other tasks
                break
            counter += 1
            if not job.run():
                self.__failure += 1
                failure += 1
            else:
                self.__suceess += 1
                suceess += 1
        logger.debug("Task thread %s is stopped, %s", current_thread().name,
                     f"{counter} jobs: {suceess} suceess and {failure} failure"
                     )

    def submit(self, fn: Callable, *args: Any, **kwargs: Any) -> TaskJob:
        '''submit a task to jobs queue

        Returns:
            int: job id
        '''
        sn: int  # serial number
        with self.__intlock:  # generate job id under lock protection
            self.__counter += 1
            sn = self.__counter
        job: TaskJob = TaskJob(sn, fn, *args, **kwargs)
        self.jobs.put(job, block=True)
        self.setdefault(sn, job)
        assert self[sn] is job
        return job

    def shutdown(self) -> None:
        '''stop all task threads and waiting for all jobs finish'''
        with self.__intlock:  # block submit new tasks
            self.cmds.logger.debug("Shutdown %s tasks", self.thread_name_prefix)  # noqa:E501
            self.__running = False
            self.jobs.put(None)  # notice tasks
            while len(self.threads) > 0:
                thread: Thread = self.threads.pop()
                thread.join()
            while not self.jobs.empty():
                job: Optional[TaskJob] = self.jobs.get(block=True)
                if job is not None:  # shutdown only after executed
                    raise RuntimeError(f"Unexecuted job: {job}")  # noqa:E501, pragma: no cover

    def startup(self) -> None:
        '''start task threads'''
        with self.__intlock:
            self.cmds.logger.debug("Startup %s tasks", self.thread_name_prefix)
            for i in range(self.workers):
                thread_name: str = f"{self.thread_name_prefix}_{i}"
                thread = Thread(name=thread_name, target=self.task)
                self.threads.add(thread)
                thread.start()  # run
            self.__running = True

    def barrier(self) -> None:
        '''stop submit new tasks and waiting for all submitted tasks to end'''
        self.shutdown()
        self.startup()
