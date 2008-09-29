#!/usr/bin/env python

import unittest
from tests import TestCase
from modipyd.tools import generic


class TestGenericTool(TestCase):

    def test_startup_files(self):
        files = list(generic.startup_files(""))
        self.assertNotNone(files)

    def test_make_application(self):
        parser = generic.make_option_parser()
        options, args = parser.parse_args([])
        application = generic.make_application(options, args or '.')
        self.assertNotNone(application)


class TestGenericToolOptions(TestCase):

    def parse_options(self, args):
        parser = generic.make_option_parser()
        self.assertNotNone(parser)
        return parser.parse_args(args)
        
    def test_empty(self):
        options, args = self.parse_options([])
        self.assertEqual(0, len(args))
        self.assertEqual(0, options.verbosity)
        self.assertEqual(0, len(options.plugins))
        self.assertNone(options.rcfile)

    def test_verbosity(self):
        options, args = self.parse_options(['-v'])
        self.assertEqual(1, options.verbosity)
        options, args = self.parse_options(['-vv'])
        self.assertEqual(2, options.verbosity)

    def test_plugins(self):
        options, args = self.parse_options([
            '-x', 'plugin1'])
        self.assertEqual(1, len(options.plugins))
        self.assertEqual('plugin1', options.plugins[0])

        options, args = self.parse_options([
            '-x', 'plugin1', '--plugin', 'plugin2'])
        self.assertEqual(2, len(options.plugins))
        self.assertEqual('plugin1', options.plugins[0])
        self.assertEqual('plugin2', options.plugins[1])


if __name__ == '__main__':
    unittest.main()
