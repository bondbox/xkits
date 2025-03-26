# coding:utf-8

import unittest
from unittest import mock

from xkits import meter


class TestTimeMeter(unittest.TestCase):

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

    @mock.patch.object(meter, "time")
    def test_runtime(self, mock_time):
        mock_time.side_effect = [1.0, 2.0, 3.0, 4.0, 5.0]
        timer = meter.TimeMeter(start=False)
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 0.0)
        self.assertEqual(timer.stopped_time, 0.0)
        self.assertEqual(timer.runtime, 0.0)
        timer.startup()
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 2.0)
        self.assertEqual(timer.stopped_time, 0.0)
        self.assertEqual(timer.runtime, 1.0)
        self.assertEqual(timer.runtime, 2.0)
        self.assertEqual(timer.runtime, 3.0)

    @mock.patch.object(meter, "time")
    def test_restart(self, mock_time):
        mock_time.side_effect = [1.0, 2.0, 3.0]
        timer = meter.TimeMeter(start=True)
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 1.0)
        self.assertEqual(timer.stopped_time, 0.0)
        timer.restart()
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 2.0)
        self.assertEqual(timer.stopped_time, 0.0)
        timer.restart()
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 3.0)
        self.assertEqual(timer.stopped_time, 0.0)

    @mock.patch.object(meter, "time")
    def test_startup(self, mock_time):
        mock_time.side_effect = [1.0, 2.0]
        timer = meter.TimeMeter(start=False)
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 0.0)
        self.assertEqual(timer.stopped_time, 0.0)
        timer.startup()
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 2.0)
        self.assertEqual(timer.stopped_time, 0.0)
        timer.startup()
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 2.0)
        self.assertEqual(timer.stopped_time, 0.0)

    @mock.patch.object(meter, "time")
    def test_shutdown(self, mock_time):
        mock_time.side_effect = [1.0, 2.0]
        timer = meter.TimeMeter(start=True)
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 1.0)
        self.assertEqual(timer.stopped_time, 0.0)
        timer.shutdown()
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 1.0)
        self.assertEqual(timer.stopped_time, 2.0)
        timer.shutdown()
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 1.0)
        self.assertEqual(timer.stopped_time, 2.0)

    @mock.patch.object(meter, "time")
    def test_reset(self, mock_time):
        mock_time.side_effect = [1.0]
        timer = meter.TimeMeter(start=True)
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 1.0)
        self.assertEqual(timer.stopped_time, 0.0)
        timer.reset()
        self.assertEqual(timer.created_time, 1.0)
        self.assertEqual(timer.started_time, 0.0)
        self.assertEqual(timer.stopped_time, 0.0)


class TestDownMeter(unittest.TestCase):

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

    @mock.patch.object(meter, "time")
    def test_downtime(self, mock_time):
        mock_time.side_effect = [1.0, 2.0, 3.0, 4.0, 5.0]
        countdown = meter.DownMeter(lifetime=3)
        self.assertEqual(countdown.created_time, 1.0)
        self.assertEqual(countdown.started_time, 1.0)
        self.assertEqual(countdown.stopped_time, 0.0)
        self.assertEqual(countdown.lifetime, 3.0)
        self.assertEqual(countdown.downtime, 2.0)
        self.assertEqual(countdown.downtime, 1.0)
        self.assertEqual(countdown.downtime, 0.0)
        self.assertEqual(countdown.downtime, -1.0)

    @mock.patch.object(meter, "time")
    def test_downtime_0(self, mock_time):
        mock_time.side_effect = [1.0]
        countdown = meter.DownMeter(lifetime=0)
        self.assertEqual(countdown.created_time, 1.0)
        self.assertEqual(countdown.started_time, 1.0)
        self.assertEqual(countdown.stopped_time, 0.0)
        self.assertEqual(countdown.lifetime, 0.0)
        self.assertEqual(countdown.downtime, 0.0)
        self.assertFalse(countdown.expired)
        self.assertFalse(countdown.expired)
        self.assertFalse(countdown.expired)

    @mock.patch.object(meter, "time")
    def test_expired(self, mock_time):
        mock_time.side_effect = [1.0, 2.0, 3.0, 4.0, 5.0]
        countdown = meter.DownMeter(lifetime=3)
        self.assertEqual(countdown.created_time, 1.0)
        self.assertEqual(countdown.started_time, 1.0)
        self.assertEqual(countdown.stopped_time, 0.0)
        self.assertEqual(countdown.lifetime, 3.0)
        self.assertFalse(countdown.expired)
        self.assertFalse(countdown.expired)
        self.assertFalse(countdown.expired)
        self.assertTrue(countdown.expired)

    @mock.patch.object(meter, "time")
    def test_reset(self, mock_time):
        mock_time.side_effect = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        countdown = meter.DownMeter(lifetime=1)
        self.assertEqual(countdown.created_time, 1.0)
        self.assertEqual(countdown.started_time, 1.0)
        self.assertEqual(countdown.stopped_time, 0.0)
        self.assertEqual(countdown.lifetime, 1.0)
        self.assertEqual(countdown.downtime, 0.0)
        countdown.reset()
        self.assertEqual(countdown.created_time, 1.0)
        self.assertEqual(countdown.started_time, 3.0)
        self.assertEqual(countdown.stopped_time, 0.0)
        self.assertEqual(countdown.lifetime, 1.0)
        self.assertEqual(countdown.downtime, 0.0)
        countdown.reset()
        self.assertEqual(countdown.created_time, 1.0)
        self.assertEqual(countdown.started_time, 5.0)
        self.assertEqual(countdown.stopped_time, 0.0)
        self.assertEqual(countdown.lifetime, 1.0)
        self.assertEqual(countdown.downtime, 0.0)

    @mock.patch.object(meter, "time")
    def test_renew(self, mock_time):
        mock_time.side_effect = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        countdown = meter.DownMeter(lifetime=1)
        self.assertEqual(countdown.created_time, 1.0)
        self.assertEqual(countdown.started_time, 1.0)
        self.assertEqual(countdown.stopped_time, 0.0)
        self.assertEqual(countdown.lifetime, 1.0)
        self.assertEqual(countdown.downtime, 0.0)
        countdown.renew(lifetime=2)
        self.assertEqual(countdown.created_time, 1.0)
        self.assertEqual(countdown.started_time, 3.0)
        self.assertEqual(countdown.stopped_time, 0.0)
        self.assertEqual(countdown.lifetime, 2.0)
        self.assertEqual(countdown.downtime, 1.0)
        countdown.renew()
        self.assertEqual(countdown.created_time, 1.0)
        self.assertEqual(countdown.started_time, 5.0)
        self.assertEqual(countdown.stopped_time, 0.0)
        self.assertEqual(countdown.lifetime, 2.0)
        self.assertEqual(countdown.downtime, 1.0)


if __name__ == "__main__":
    unittest.main()
