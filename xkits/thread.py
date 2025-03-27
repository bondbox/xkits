# coding:utf-8

from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import sys
from threading import Lock
from threading import Thread
from threading import current_thread  # noqa:H306
from time import sleep
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generic
from typing import Iterator
from typing import Optional
from typing import Set
from typing import Tuple
from typing import TypeVar

from xkits.actuator import Logger
from xkits.actuator import commands  # noqa:H306
from xkits.meter import CountMeter
from xkits.meter import StatusCountMeter
from xkits.meter import TimeMeter
from xkits.meter import TimeUnit

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


class TaskJob():
    '''Task Job'''

    def __init__(self, no: int, fn: Callable, *args: Any, **kwargs: Any):
        self.__no: int = no
        self.__fn: Callable = fn
        self.__args: Tuple[Any, ...] = args
        self.__kwargs: Dict[str, Any] = kwargs
        self.__result: Any = LookupError(f"{self} is not started")
        self.__running_timer: TimeMeter = TimeMeter(startup=False)

    @classmethod
    def create_task(cls, fn: Callable, *args: Any, **kwargs: Any) -> "TaskJob":
        return cls(-1, fn, *args, **kwargs)

    def __str__(self) -> str:
        args = list(self.args) + list(f"{k}={v}" for k, v in self.kwargs)
        info: str = ", ".join(f"{a}" for a in args)
        return f"{self.__class__.__name__}{self.id} {self.fn}({info})"

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
    def running_timer(self) -> TimeMeter:
        '''job running timer'''
        return self.__running_timer

    def run(self) -> bool:
        '''run job'''
        try:
            if self.running_timer.started:
                raise RuntimeError(f"{self} is already started")
            assert not self.running_timer.started, f"{self} is already started"
            self.running_timer.startup()
            assert self.running_timer.started, f"failed to start {self}"
            self.__result = self.fn(*self.args, **self.kwargs)
            return True
        except Exception as error:  # pylint: disable=broad-exception-caught
            self.__result = error
            return False
        finally:
            self.running_timer.shutdown()

    def shutdown(self) -> None:
        '''wait for job to finish'''
        while self.running_timer.started:
            sleep(0.05)

    def startup(self) -> None:
        '''same as run'''
        self.run()

    def restart(self) -> None:
        '''restart job'''
        self.shutdown()
        self.startup()

    def barrier(self) -> None:
        '''same as shutdown'''
        self.shutdown()


class DelayTaskJob(TaskJob):
    '''Delay Task Job'''
    MIN_DELAY_TIME: float = 0.001

    def __init__(self, delay: TimeUnit, no: int, fn: Callable, *args: Any, **kwargs: Any):  # noqa:E501
        self.__delay_time: float = float(max(delay, self.MIN_DELAY_TIME))
        self.__delay_timer: TimeMeter = TimeMeter(startup=True)
        super().__init__(no, fn, *args, **kwargs)

    @classmethod
    def create_delay_task(cls, delay: TimeUnit, fn: Callable, *args: Any, **kwargs: Any) -> "DelayTaskJob":  # noqa:E501
        return cls(delay, -1, fn, *args, **kwargs)

    @property
    def delay_timer(self) -> TimeMeter:
        '''job delay timer'''
        return self.__delay_timer

    @property
    def delay_time(self) -> float:
        '''job delay time'''
        return self.__delay_time

    @property
    def waiting(self) -> bool:
        '''job waiting to run'''
        return self.delay_timer.runtime < self.delay_time

    def renew(self, delay: Optional[TimeUnit] = None) -> None:
        '''renew delay time'''
        if delay is not None:
            self.__delay_time = float(max(delay, self.MIN_DELAY_TIME))
        self.delay_timer.restart()

    def run(self) -> bool:
        '''run delay job'''
        self.delay_timer.alarm(self.delay_time)
        assert not self.waiting, f"{self} is waiting to run"
        return super().run()


class DaemonTaskJob(TaskJob):
    '''Daemon Task Job'''

    def __init__(self, no: int, fn: Callable, *args: Any, **kwargs: Any):
        self.__counter: StatusCountMeter = StatusCountMeter()
        super().__init__(no, fn, *args, **kwargs)
        self.__running: bool = False

    @classmethod
    def create_daemon_task(cls, fn: Callable, *args: Any, **kwargs: Any) -> "DaemonTaskJob":  # noqa:E501
        return cls(-1, fn, *args, **kwargs)

    @property
    def daemon_counter(self) -> StatusCountMeter:
        '''daemon status counter'''
        return self.__counter

    @property
    def daemon_running(self) -> bool:
        '''daemon running flag'''
        return self.__running

    def run_in_background(self) -> Thread:
        '''run job in daemon mode in background'''
        thread: Thread = Thread(target=self.run)
        thread.start()
        return thread

    def run(self):
        '''run job in daemon mode'''
        self.__running = True
        while self.daemon_running:
            success: bool = super().run()
            self.daemon_counter.inc(success)

    def shutdown(self) -> None:
        '''wait for job to finish'''
        self.__running = False
        super().shutdown()

    def startup(self) -> None:
        '''same as run in background'''
        self.run_in_background()

    def restart(self) -> None:
        '''restart job'''
        self.shutdown()
        self.startup()

    def barrier(self) -> None:
        '''same as restart'''
        self.restart()


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
        self.__status: StatusCountMeter = StatusCountMeter()
        self.__counter: CountMeter = CountMeter()
        self.__threads: Set[Thread] = set()
        self.__intlock: Lock = Lock()  # internal lock
        self.__running: bool = False
        self.__workers: int = wsize
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
    def status_counter(self) -> StatusCountMeter:
        '''task job status counter'''
        return self.__status

    def task(self):
        '''execute a task from jobs queue'''
        status_counter: StatusCountMeter = StatusCountMeter()

        logger: Logger = self.cmds.logger
        logger.debug("Task thread %s is running", current_thread().name)

        while True:
            job: Optional[TaskJob] = self.jobs.get(block=True)
            if job is None:  # stop task
                self.jobs.put(job)  # notice other tasks
                break

            if isinstance(job, DelayTaskJob) and job.waiting and self.running:
                self.jobs.put(job)  # delay run task
                continue

            if not job.run():
                self.status_counter.inc(False)
                status_counter.inc(False)
            else:
                self.status_counter.inc(True)
                status_counter.inc(True)

        logger.debug("Task thread %s is stopped, %s", current_thread().name,
                     f"{status_counter.total} jobs: {status_counter.success} success and {status_counter.failure} failure")  # noqa:E501

    def submit_job(self, job: TaskJob) -> TaskJob:
        assert isinstance(job, TaskJob), f"{job} is not a TaskJob"
        assert job.id not in self, f"{job} id is already in pool"
        assert job.id > 0, f"{job} id is invalid"
        self.jobs.put(job, block=True)
        self.setdefault(job.id, job)
        return job

    def submit_task(self, fn: Callable, *args: Any, **kwargs: Any) -> TaskJob:
        '''submit a task to jobs queue'''
        with self.__intlock:  # generate job id under lock protection
            sn: int = self.__counter.inc()  # serial number
            return self.submit_job(TaskJob(sn, fn, *args, **kwargs))

    def submit_delay_task(self, delay: TimeUnit, fn: Callable, *args: Any, **kwargs: Any) -> TaskJob:  # noqa:E501
        '''submit a delay task to jobs queue'''
        with self.__intlock:  # generate job id under lock protection
            sn: int = self.__counter.inc()  # serial number
            return self.submit_job(DelayTaskJob(delay, sn, fn, *args, **kwargs))  # noqa:E501

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

    def restart(self) -> None:
        '''stop submit new tasks and waiting for all submitted tasks to end'''
        self.shutdown()
        self.startup()

    def barrier(self) -> None:
        '''same as restart'''
        self.restart()
