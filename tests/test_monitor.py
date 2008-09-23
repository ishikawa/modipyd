#!/usr/bin/env python

import unittest
from os.path import join
from modipyd.monitor import ModuleMonitor
from modipyd.module import Module, compile_source, \
                           collect_python_module, \
                           read_python_module
from tests import TestCase, FILES_DIR


class TestModipydMonitor(TestCase):

    def test_init(self):
        filepath = join(FILES_DIR, 'python', 'a.py')
        module = read_python_module(filepath, [FILES_DIR])

        self.assertNotNone(module)
        monitor = ModuleMonitor(module)

        self.assertEqual('python.a', monitor.name)
        self.assertEqual(filepath, monitor.filepath)


if __name__ == '__main__':
    unittest.main()
