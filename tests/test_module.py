#!/usr/bin/env python

import unittest
from os.path import join
import modipyd.module
from tests import TestCase, FILES_DIR


class TestModipydModule(TestCase):

    def test_init(self):
        py = join(FILES_DIR, 'python', 'a.py')
        code = modipyd.module.compile_source(py)
        self.assertNotNone(code)

        module = modipyd.module.Module('a', py, code)
        self.assertNotNone(module)
        self.assertEqual(0, len(module.imports))


if __name__ == '__main__':
    unittest.main()
