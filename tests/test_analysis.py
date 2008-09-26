#!/usr/bin/env python

import unittest
from os.path import join
from modipyd.descriptor import build_module_descriptors
from modipyd.module import collect_module_code
from modipyd.analysis import has_subclass
from tests import TestCase, FILES_DIR


class TestAnalysisModule(TestCase):

    def setUp(self):
        self.search_path = join(FILES_DIR, 'autotest')
        codes = list(collect_module_code(
            self.search_path, self.search_path))
        self.descriptors = build_module_descriptors(codes)

    def test_module_in_package(self):
        mod = self.descriptors['tests.a']
        self.assert_(has_subclass(mod, unittest.TestCase))

    def test_module_not_in_package(self):
        test_script = self.descriptors['test_script']
        self.assert_(has_subclass(test_script, unittest.TestCase))

    def test_package_relative_imports(self):
        mod = self.descriptors['tests.B.b']
        self.assert_(has_subclass(mod, unittest.TestCase))

        mod = self.descriptors['tests.B']
        self.assert_(has_subclass(mod, unittest.TestCase))


if __name__ == '__main__':
    unittest.main()
