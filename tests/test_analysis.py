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

    def import_modules(self, path):
        sys.path.insert(0, path)
        codes = list(collect_module_code(path, path))
        self.descriptors.update(build_module_descriptors(codes))

    def setUp(self):
        self.syspath = sys.path[:]
        self.descriptors = {}
        self.import_modules(join(FILES_DIR, 'autotest'))
        if HAS_RELATIVE_IMPORTS:
            self.import_modules(join(FILES_DIR, 'relative_imports'))

    def tearDown(self):
        sys.path = self.syspath

    def test_illegal_argument(self):
        mod = self.descriptors['tests_module']
        self.assertRaises(TypeError, has_subclass, mod, 12345)

    def test_module_in_package(self):
        mod = self.descriptors['tests_module']
        self.assert_(has_subclass(mod, unittest.TestCase))
        mod = self.descriptors['tests_module.a']
        self.assert_(has_subclass(mod, unittest.TestCase))
        mod = self.descriptors['tests_module.a2']
        self.assert_(has_subclass(mod, unittest.TestCase))

    def test_mixed_modules(self):
        mod = self.descriptors['tests_module.mixed']
        self.assert_(has_subclass(mod, unittest.TestCase))

    def test_module_not_in_package(self):
        test_script = self.descriptors['test_script']
        self.assert_(has_subclass(test_script, unittest.TestCase))

    def test_package_relative_imports(self):
        if not HAS_RELATIVE_IMPORTS:
            return

        mod = self.descriptors['RA.RB.b']
        self.assert_(has_subclass(mod, unittest.TestCase))

        mod = self.descriptors['RA.RB.b2']
        self.assert_(has_subclass(mod, unittest.TestCase))

        mod = self.descriptors['RA.RB.b3']
        self.assert_(has_subclass(mod, unittest.TestCase))

        mod = self.descriptors['RA.RB']
        self.assert_(has_subclass(mod, unittest.TestCase))


if __name__ == '__main__':
    unittest.main()
