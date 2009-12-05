#!/usr/bin/env python

import unittest
from tests import TestCase
import logging

from modipyd import LOGGER
from modipyd.tools import autotest
from modipyd.application.plugins import Autotest

from modipyd.monitor import Event, Monitor
from modipyd.descriptor import ModuleDescriptor
from modipyd.module import read_module_code


class FakeAutotest(Autotest):

    def spawn_unittest_runner(self, testables, extra_arguments=None):
        self.testables = testables
        self.extra_arguments = extra_arguments


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

    def test_autotest_plugin(self):
        monitor = Monitor(__file__)
        descriptor = ModuleDescriptor(read_module_code(__file__))
        event = Event(Event.MODULE_MODIFIED, descriptor)
        plugin = FakeAutotest(event, monitor, {});

        self.assertEqual(descriptor, plugin.descriptor)
        self.assertTrue(callable(plugin))

        plugin()
        self.assertEqual([descriptor], plugin.testables)
        self.assertEqual(['--loglevel', LOGGER.getEffectiveLevel()], plugin.extra_arguments)


if __name__ == '__main__':
    unittest.main()
