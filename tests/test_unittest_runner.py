#!/usr/bin/env python

import unittest
import tests
from modipyd.tools.unittest_runner import collect_unittest


class TestUnitTestRunner(tests.TestCase):

    def test_collect_unittest(self):
        suite = collect_unittest(__file__)
        self.assertEqual( 1, suite.countTestCases() )

