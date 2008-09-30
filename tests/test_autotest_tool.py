#!/usr/bin/env python

import unittest
from tests import TestCase
from modipyd.tools import autotest
from modipyd.application.plugins import Autotest


class TestAutotestTool(TestCase):

    def parse_options(self, args):
        parser = autotest.make_option_parser()
        self.assertNotNone(parser)
        return parser.parse_args(args)

    def make_application(self, args):
        options, args = self.parse_options(args)
        return autotest.make_application(options, args or '.')

    def test_application(self):
        application = self.make_application([])
        self.assertEqual(1, len(application.plugins))
        self.assertEqual(Autotest, application.plugins[0])

    def test_runner_option(self):
        application = self.make_application([
            '-r', 'myproject.unittest.TestRunner'])
        self.assert_(
            Autotest.CONTEXT_TEST_RUNNER in application.variables)
        self.assertEqual(
            'myproject.unittest.TestRunner',
            application.variables[Autotest.CONTEXT_TEST_RUNNER])


if __name__ == '__main__':
    unittest.main()
