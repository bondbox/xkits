# coding:utf-8

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

        job: TaskJob = DelayTaskJob(1.0, 1, handle, False)
        self.assertRaises(LookupError, result, job)
        self.assertLess(job.created_time, time())
        self.assertEqual(job.started_time, 0.0)
        self.assertEqual(job.stopped_time, 0.0)
        self.assertFalse(job.started)
        self.assertFalse(job.stopped)
        self.assertEqual(job.id, 1)
        self.assertTrue(job.run())
        self.assertFalse(job.result)
        self.assertIsNone(job.renew(1.0))
        self.assertLess(job.created_time, time())
        self.assertLess(job.started_time, time())
        self.assertLess(job.stopped_time, time())
        self.assertFalse(job.started)
        self.assertTrue(job.stopped)
        self.assertTrue(job.run())
        job.startup()
        self.assertTrue(job.started)
        self.assertFalse(job.stopped)
        self.assertFalse(job.run())

    def test_task(self):
        def lock(tasker: TaskPool, index: int):
            tasker.cmds.stdout(f"{index}")
            if index % 2 == 1:
                raise Exception(f"task{index}")
        with TaskPool(8) as tasker:
            for index in range(15):
                tasker.submit(lock, tasker, index)
            tasker.barrier()
            self.assertEqual(tasker.counter, 15)
            self.assertEqual(tasker.suceess, 8)
            self.assertEqual(tasker.failure, 7)
            self.assertTrue(tasker.running)
            tasker.shutdown()
            self.assertFalse(tasker.running)
            tasker.startup()
            self.assertTrue(tasker.running)


if __name__ == "__main__":
    unittest.main()
