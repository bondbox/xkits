# coding:utf-8

from time import sleep
from time import time
import unittest

from xkits import DelayTaskJob
from xkits import NamedLock
from xkits import TaskJob
from xkits import TaskPool
from xkits import ThreadPool


class test_named_lock(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.namedlock: NamedLock[str] = NamedLock()
        cls.lockname: str = "test"

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_lock(self):
        self.assertEqual(len(self.namedlock), 0)
        self.assertNotIn(self.lockname, self.namedlock)
        self.assertIsInstance(self.namedlock.lookup(self.lockname), NamedLock.LockItem)  # noqa:E501
        self.assertEqual(len(self.namedlock), 1)
        self.assertIn(self.lockname, self.namedlock)
        for lock in self.namedlock:
            with lock.lock:
                self.assertIs(self.namedlock[lock.name], lock.lock)


class test_thread_pool(unittest.TestCase):

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

    def test_join(self):
        def handle() -> bool:
            return True

        with ThreadPool(1) as pool:
            pool.submit(handle)
            pool.submit(handle)
            pool.submit(handle)
            pool.submit(handle)
            pool.submit(handle)
            pool.cmds.stdout("unittest")
            self.assertIsInstance(pool.alive_threads, set)
            self.assertIsInstance(pool.other_threads, set)
            self.assertIsInstance(pool.other_alive_threads, set)
            pool.shutdown()


class test_task_pool(unittest.TestCase):

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

    def test_job(self):
        def handle(value: bool) -> bool:
            return value

        def result(job: TaskJob):
            return job.result

        self.assertIsInstance(DelayTaskJob.create_task(handle, False), TaskJob)
        job: DelayTaskJob = DelayTaskJob.create_delay_task(0.01, handle, False)
        self.assertIsInstance(job, DelayTaskJob)
        self.assertRaises(LookupError, result, job)
        self.assertLess(job.running_timer.created_time, time())
        self.assertEqual(job.running_timer.started_time, 0.0)
        self.assertEqual(job.running_timer.stopped_time, 0.0)
        self.assertFalse(job.running_timer.started)
        self.assertFalse(job.running_timer.stopped)
        self.assertEqual(job.id, -1)
        self.assertTrue(job.run())
        self.assertFalse(job.result)
        self.assertIsNone(job.renew(1.0))
        self.assertLess(job.running_timer.created_time, time())
        self.assertLess(job.running_timer.started_time, time())
        self.assertLess(job.running_timer.stopped_time, time())
        self.assertFalse(job.running_timer.started)
        self.assertTrue(job.running_timer.stopped)
        self.assertIsNone(job.barrier())
        self.assertIsNone(job.restart())
        job.running_timer.startup()
        self.assertTrue(job.running_timer.started)
        self.assertFalse(job.running_timer.stopped)
        self.assertFalse(job.run())
        self.assertFalse(job.running_timer.started)
        self.assertTrue(job.running_timer.stopped)

        def sleep_task(seconds: float = 1.0):
            sleep(seconds)

        def run_job(job: TaskJob):
            job.run()

        with ThreadPool(1) as pool:
            task: TaskJob = TaskJob.create_task(sleep_task, 0.5)
            pool.submit(run_job, task)
            task.shutdown()

    def test_task(self):
        def lock(tasker: TaskPool, index: int):
            tasker.cmds.stdout(f"{index}")
            if index % 2 == 1:
                raise Exception(f"task{index}")
        with TaskPool(8) as tasker:
            tasker.submit_job(TaskJob(123456, lock, tasker, 0))
            tasker.submit_delay_task(0.01, lock, tasker, 1)
            tasker.submit_delay_task(0.01, lock, tasker, 2)
            tasker.submit_task(lock, tasker, 3)
            tasker.submit_task(lock, tasker, 4)
            tasker.barrier()
            self.assertEqual(tasker.status_counter.total, 5)
            self.assertEqual(tasker.status_counter.success, 3)
            self.assertEqual(tasker.status_counter.failure, 2)
            self.assertTrue(tasker.running)
            tasker.shutdown()
            self.assertFalse(tasker.running)
            tasker.startup()
            self.assertTrue(tasker.running)


if __name__ == "__main__":
    unittest.main()
