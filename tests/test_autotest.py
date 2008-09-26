#!/usr/bin/env python

import unittest
from os.path import join
from modipyd.descriptor import ModuleDescriptor, \
                               build_module_descriptors
from modipyd.module import collect_module_code
from modipyd.tools.autotest import testcase_module
from tests import TestCase, FILES_DIR


class TestAutotestTestCaseModule(TestCase):

    def setUp(self):
        self.search_path = join(FILES_DIR, 'autotest')
        codes = list(collect_module_code(
            self.search_path, self.search_path))
        self.descriptors = build_module_descriptors(codes)

    def test_test_script(self):
        test_script = self.descriptors['test_script']
        self.assert_(testcase_module(test_script))


if __name__ == '__main__':
    unittest.main()
