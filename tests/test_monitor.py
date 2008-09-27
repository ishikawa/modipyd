#!/usr/bin/env python
import unittest
from os.path import join, exists

from tests import TestCase, FILES_DIR
from modipyd.monitor import Monitor


class TestSimpleMonitor(TestCase):

    def setUp(self):
        self.monitor = Monitor(join(FILES_DIR, 'cycles'), [FILES_DIR])

    def test_init(self):
        self.assertNotNone(self.monitor)
        self.assert_(not self.monitor.monitoring)

    def test_start_iterator(self):
        modified_iter = self.monitor.start()
        self.assertNotNone(modified_iter)
        self.assert_(hasattr(modified_iter, 'next'))
        self.assert_(callable(modified_iter.next))

    def test_not_modified(self):
        modified = self.monitor.monitor()
        self.assertEqual(0, len(modified))


PRISONERS_DIR = join(FILES_DIR, 'prisoners')

class TestMonitor(TestCase):

    def setUp(self):
        path = join(PRISONERS_DIR, '__init__.py')
        if not exists(path):
            f = open(path, 'w')
            f.write("")
            f.close()

    def test_init(self):
        pass


if __name__ == '__main__':
    unittest.main()
