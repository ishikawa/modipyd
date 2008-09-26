#!/usr/bin/env python

import sys
import unittest
from os.path import join
from modipyd import HAS_RELATIVE_IMPORTS
from modipyd.descriptor import build_module_descriptors
from modipyd.module import collect_module_code
from modipyd.analysis import has_subclass
from tests import TestCase, FILES_DIR


class TestAnalysisModule(TestCase):

    def setUp(self):
        self.syspath = sys.path[:]

        if HAS_RELATIVE_IMPORTS:
            self.search_path = join(FILES_DIR, 'autotest')
        else:
            self.search_path = join(FILES_DIR, 'autotest24')
        sys.path.insert(0, self.search_path)

        codes = list(collect_module_code(
            self.search_path, self.search_path))
        self.descriptors = build_module_descriptors(codes)

    def tearDown(self):
        sys.path = self.syspath

    def test_module_in_package(self):
        mod = self.descriptors['tests_module']
        self.assert_(has_subclass(mod, unittest.TestCase))
        mod = self.descriptors['tests_module.a']
        self.assert_(has_subclass(mod, unittest.TestCase))
        mod = self.descriptors['tests_module.a2']
        self.assert_(has_subclass(mod, unittest.TestCase))

    def test_module_not_in_package(self):
        test_script = self.descriptors['test_script']
        self.assert_(has_subclass(test_script, unittest.TestCase))

    def test_package_relative_imports(self):
        mod = self.descriptors['tests_module.B.b']
        self.assert_(has_subclass(mod, unittest.TestCase))

        mod = self.descriptors['tests_module.B.b2']
        self.assert_(has_subclass(mod, unittest.TestCase))

        mod = self.descriptors['tests_module.B.b3']
        self.assert_(has_subclass(mod, unittest.TestCase))

        mod = self.descriptors['tests_module.B']
        self.assert_(has_subclass(mod, unittest.TestCase))


if __name__ == '__main__':
    unittest.main()
