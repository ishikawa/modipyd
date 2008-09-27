#!/usr/bin/env python
import unittest
from os.path import join

from tests import TestCase, FILES_DIR
from modipyd.monitor import Monitor


class TestModipydMonitor(TestCase):

    def test_init(self):
        monitor = Monitor(join(FILES_DIR, 'cycles'), [FILES_DIR])
        self.assertNotNone(monitor)
        self.assert_(not monitor.monitoring)


if __name__ == '__main__':
    unittest.main()
