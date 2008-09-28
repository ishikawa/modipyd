#!/usr/bin/env python
import unittest
import time
import os
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

    def mkfiles(self):
        # __init__.py
        f = open(join(PRISONERS_DIR, '__init__.py'), 'w')
        try:
            f.write("from prisoners.b import money")
        finally:
            f.close()

        # a.py
        f = open(join(PRISONERS_DIR, 'a.py'), 'w')
        try:
            f.write("")
        finally:
            f.close()

        # b.py
        f = open(join(PRISONERS_DIR, 'b.py'), 'w')
        try:
            f.write("""\
money = 4321.09
""")
        finally:
            f.close()

        # c.py
        path = join(PRISONERS_DIR, 'c.py')
        if exists(path):
            os.remove(path)

    def setUp(self):
        self.mkfiles()
        self.monitor = Monitor(PRISONERS_DIR, [FILES_DIR])

    def test_init(self):
        self.assertNotNone(self.monitor)
        descriptors = self.monitor.descriptors

        self.assertNotNone(self.monitor.descriptors)
        self.assertEqual(3, len(descriptors))
        self.assert_('prisoners' in descriptors)
        self.assert_('prisoners.a' in descriptors)
        self.assert_('prisoners.b' in descriptors)

    def test_init_dependencies(self):
        descriptors = self.monitor.descriptors
        init = descriptors['prisoners']
        a = descriptors['prisoners.a']
        b = descriptors['prisoners.b']

        self.assertEqual(1, len(init.dependencies))
        self.assert_(b in init.dependencies)
        self.assertEqual(0, len(init.reverse_dependencies))

        self.assertEqual(0, len(a.dependencies))
        self.assertEqual(0, len(a.reverse_dependencies))

        self.assertEqual(0, len(b.dependencies))
        self.assertEqual(1, len(b.reverse_dependencies))

    def test_modified(self):
        modified = self.monitor.monitor()
        self.assertEqual(0, len(modified))
        time.sleep(1)

        # modify
        f = open(join(PRISONERS_DIR, 'b.py'), 'w')
        f.write("")
        f.close()
        time.sleep(0.1)

        modified = self.monitor.monitor()
        self.assertEqual(1, len(modified))
        m = modified[0]
        self.assertEqual('prisoners.b', m.name)
        self.assertEqual(0, len(m.dependencies))
        self.assertEqual(1, len(m.reverse_dependencies))

    def test_deleted(self):
        os.remove(join(PRISONERS_DIR, 'a.py'))
        time.sleep(0.1)
        modified = self.monitor.monitor()
        self.assertEqual(0, len(modified))
        descriptors = self.monitor.descriptors
        self.assertEqual(2, len(descriptors))

    def test_refresh(self):
        descriptors = self.monitor.descriptors
        self.assertEqual(3, len(descriptors))

        a = descriptors['prisoners.a']
        self.assertEqual(0, len(a.dependencies))
        self.assertEqual(0, len(a.reverse_dependencies))

        # create new file
        path = join(PRISONERS_DIR, 'c.py')
        f = open(path, 'w')
        try:
            f.write("import prisoners.a")
        finally:
            f.close()
            time.sleep(0.1)
            assert exists(path)

        self.monitor.refresh()
        self.assertEqual(4, len(descriptors))
        a = descriptors['prisoners.a']
        c = descriptors['prisoners.c']

        self.assertEqual(0, len(a.dependencies))
        self.assertEqual(1, len(a.reverse_dependencies))
        self.assertEqual(1, len(c.dependencies))
        self.assertEqual(0, len(c.reverse_dependencies))

        # remove file
        os.remove(path)
        time.sleep(0.1)
        assert not exists(path)
        self.monitor.refresh()
        self.assertEqual(3, len(descriptors))

        a = descriptors['prisoners.a']
        self.assertEqual(0, len(a.dependencies))
        self.assertEqual(0, len(a.reverse_dependencies))
        self.assert_('prisoners.c' not in descriptors)


if __name__ == '__main__':
    unittest.main()
