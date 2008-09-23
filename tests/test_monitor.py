#!/usr/bin/env python

import unittest
from os.path import join
from modipyd.monitor import ModuleDescriptor, build_module_descriptors
from modipyd.module import collect_python_module, \
                           read_python_module
from tests import TestCase, FILES_DIR


class TestModipydMonitor(TestCase):

    def test_init(self):
        filepath = join(FILES_DIR, 'python', 'a.py')
        module = read_python_module(filepath, [FILES_DIR])

        self.assertNotNone(module)
        monitor = ModuleDescriptor(module)

        self.assertEqual('python.a', monitor.name)
        self.assertEqual(filepath, monitor.filepath)

    def test_dependency(self):

        modules = list(collect_python_module(
            join(FILES_DIR, 'cycles'),
            [FILES_DIR]))
        modules = build_module_descriptors(modules)

        # file existence check
        names = set(modules.keys())
        names.remove('cycles')
        names.remove('cycles.a')
        names.remove('cycles.b')
        names.remove('cycles.c')
        names.remove('cycles.d')
        names.remove('cycles.e')
        names.remove('cycles.f')
        self.assertEqual(0, len(names))

        # dependency
        a = modules['cycles.a']
        self.assertEqual(1, len(a.dependencies))
        self.assertEqual(modules['cycles.d'], a.dependencies[0])
        self.assertEqual(1, len(a.reverse_dependencies))
        self.assertEqual(modules['cycles.b'], a.reverse_dependencies[0])


if __name__ == '__main__':
    unittest.main()
