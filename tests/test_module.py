#!/usr/bin/env python

import unittest
from os.path import join
from modipyd.module import Module, compile_source, \
                           collect_python_module
from tests import TestCase, FILES_DIR


class TestModipydModule(TestCase):

    def test_init(self):
        py = join(FILES_DIR, 'python', 'a.py')
        code = compile_source(py)
        self.assertNotNone(code)

        module = Module('a', py, code)
        self.assertNotNone(module)
        self.assertEqual(0, len(module.imports))

    def test_collect_python_module(self):
        modules = list(collect_python_module(
            join(FILES_DIR, 'python'),
            [FILES_DIR]))
        self.assertNotNone(modules)
        self.assertEqual(2, len(modules))

        names = [m.name for m in modules]
        self.assert_('python.a' in names)
        self.assert_('python' in names)


if __name__ == '__main__':
    unittest.main()
