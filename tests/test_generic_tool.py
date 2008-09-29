#!/usr/bin/env python

import unittest
from tests import TestCase
from modipyd.tools import generic


class GenericToolTestCase(TestCase):

    def parse_options(self, args):
        parser = generic.make_option_parser()
        self.assertNotNone(parser)
        return parser.parse_args(args)

    def make_application(self, args):
        parser = generic.make_option_parser()
        options, args = parser.parse_args(args)
        return generic.make_application(options, args or '.')


class TestGenericTool(GenericToolTestCase):

    def test_startup_files(self):
        files = list(generic.startup_files(""))
        self.assertNotNone(files)

    def test_make_application(self):
        application = self.make_application([])
        self.assertNotNone(application)


class TestGenericToolOptions(GenericToolTestCase):

    def test_empty(self):
        options, args = self.parse_options([])
        self.assertEqual(0, len(args))
        self.assertEqual(0, options.verbosity)
        self.assertEqual(0, len(options.plugins))
        self.assertNone(options.rcfile)

    def test_verbosity(self):
        options = self.parse_options(['-v'])[0]
        self.assertEqual(1, options.verbosity)
        options = self.parse_options(['-vv'])[0]
        self.assertEqual(2, options.verbosity)

    def test_plugins(self):
        options = self.parse_options([
            '-x', 'plugin1'])[0]
        self.assertEqual(1, len(options.plugins))
        self.assertEqual('plugin1', options.plugins[0])

        options = self.parse_options([
            '-x', 'plugin1', '--plugin', 'plugin2'])[0]
        self.assertEqual(2, len(options.plugins))
        self.assertEqual('plugin1', options.plugins[0])
        self.assertEqual('plugin2', options.plugins[1])


class TestGenericToolDefineOption(GenericToolTestCase):

    def test_define_simple_value(self):
        application = self.make_application([
            '-D', 'debug=1',
        ])

        self.assertEqual(1, len(application.variables))
        self.assert_('debug' in application.variables)
        self.assertEqual("1", application.variables['debug'])

    def test_define_value_omitted(self):
        application = self.make_application([
            '-D', 'debug',
        ])

        self.assertEqual(1, len(application.variables))
        self.assert_('debug' in application.variables)
        self.assertEqual("", application.variables['debug'])

    def test_define_value_quoted(self):
        application = self.make_application([
            '-D', 'message=Hello, World!',
        ])

        self.assertEqual(1, len(application.variables))
        self.assert_('message' in application.variables)
        self.assertEqual("Hello, World!", application.variables['message'])

    def test_define_multiple_values(self):
        application = self.make_application([
            '-D', 'debug=1',
            '-D', 'readonly',
            '-D', 'message=Hello, World!',
        ])

        self.assertEqual(3, len(application.variables))
        self.assert_('debug' in application.variables)
        self.assertEqual("1", application.variables['debug'])
        self.assert_('readonly' in application.variables)
        self.assertEqual("", application.variables['readonly'])
        self.assert_('message' in application.variables)
        self.assertEqual("Hello, World!", application.variables['message'])


if __name__ == '__main__':
    unittest.main()
