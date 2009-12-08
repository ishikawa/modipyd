#!/usr/bin/env python

import imp
import sys
import os.path
import unittest
from os.path import abspath, splitext, join, dirname

from modipyd import utils
from modipyd.resolve import ModuleNameResolver
from tests import TestCase, FILES_DIR


class TestModuleNameResolver(TestCase):

    def test_package_name(self):
        d = join(FILES_DIR, 'imports')
        d = abspath(d)
        resolver = ModuleNameResolver([d])

        for f in utils.collect_files(d):
            assert f.startswith(d)
            if not f.endswith('.py'):
                continue
            modname, package = resolver.resolve(f)

            f = f[len(d):]
            if f[0] == '/':
                f = f[1:]
            f = splitext(f)[0]
            f = f.replace('/', '.')
            if f.endswith('.__init__'):
                f = utils.split_module_name(f)[0]
                self.assertEqual(f, modname)
                self.assertEqual(f, package)
            else:
                self.assertEqual(f, modname)
                self.assertEqual(
                    utils.split_module_name(f)[0], package)

    def test_not_package(self):
        d = join(FILES_DIR, 'python3')
        path = join(d, 'c.py')
        resolver = ModuleNameResolver([d])
        mod, package = resolver.resolve(path)
        self.assertEqual('c', mod)
        self.assertNone(package)

    def test_find_module(self):
        resolver = ModuleNameResolver(sys.path)

        pathname, kind = resolver._find_module('modipyd.resolve', sys.path)
        self.assert_(kind in (imp.PY_SOURCE, imp.PY_COMPILED))
        path = abspath(join(dirname(__file__), '..', 'modipyd', 'resolve.py'))
        self.assertEqual(path, pathname)

        self.assertRaises(ImportError, resolver._find_module, 'modipyd.xxx', sys.path)

    def test_name_collision(self):
        directory = join(FILES_DIR, 'name_collision')
        resolver = ModuleNameResolver(directory)

        # The package 'test' precedes 'test.py'
        path = join(directory, 'test', '__init__.py')
        modname, package = resolver.resolve(path)
        self.assertEqual('test', modname)
        self.assertEqual('test', package)

        path = join(directory, 'test.py')
        self.assert_(os.path.exists(path))
        self.assertRaises(ImportError, resolver.resolve, path)


if __name__ == '__main__':
    unittest.main()
