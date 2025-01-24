# coding:utf-8

from time import time
import unittest

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

    def test_init(self):
        pool: ThreadPool = ThreadPool(1)
        pool.cmds.stdout("unittest")
        self.assertIsInstance(pool.alive_threads, set)
        self.assertIsInstance(pool.other_threads, set)
        self.assertIsInstance(pool.other_alive_threads, set)


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

        job: TaskJob = TaskJob(1, handle, False)
        self.assertRaises(LookupError, result, job)
        self.assertLess(job.created, time())
        self.assertEqual(job.started, 0.0)
        self.assertEqual(job.stopped, 0.0)
        self.assertEqual(job.id, 1)
        self.assertTrue(job.run())
        self.assertFalse(job.result)
        self.assertLess(job.created, time())
        self.assertLess(job.started, time())
        self.assertLess(job.stopped, time())
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
