#!/usr/bin/env python

import unittest
import os
import sys
from os.path import join, dirname

from modipyd import utils
from tests import TestCase, FILES_DIR


class TestModipydUtils(TestCase):

    def test_wrap_sequence(self):
        self.assertEqual([], utils.wrap_sequence([]))
        self.assertEqual([1, 2, 3], utils.wrap_sequence([1, 2, 3]))
        self.assertEqual((1,), utils.wrap_sequence(1))
        self.assertEqual([1], utils.wrap_sequence(1, list))

    def test_is_python_module_file(self):
        filepath = join(FILES_DIR, '000/001')
        script = join(FILES_DIR, 'python/a.py')

        assert os.path.exists(filepath)
        assert os.path.exists(script)

        self.assert_(not utils.is_python_module_file(None))
        self.assert_(not utils.is_python_module_file(""))

        self.assert_(utils.is_python_module_file(script),
            "Expected python file: %s" % script)
        self.assert_(not utils.is_python_module_file(filepath),
            "Expected not python file: %s" % filepath)
        self.assert_(not utils.is_python_module_file("not_found_file"))


class TestDetectModulename(TestCase):

    def test_empty(self):
        self.assertRaises(RuntimeError, utils.find_modulename, None)
        self.assertRaises(RuntimeError, utils.find_modulename, "")

    def assert_find_modulename_in_dir(self,
                            expected_name, filepath, directory):
        name = utils.find_modulename(filepath, [directory])
        self.assertEqual(expected_name,
            name,
            "Expected module name is '%s', but was '%s' (%s in %s)" %
            (expected_name, name, filepath, directory))

        # '/'
        directory += '/'
        name = utils.find_modulename(filepath, [directory])
        self.assertEqual(expected_name,
            name,
            "Expected module name is '%s', but was '%s' (%s in %s)" %
            (expected_name, name, filepath, directory))

    def test_python_package(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, '__init__.py')
        self.assert_find_modulename_in_dir("python",
            script, dirname(python_dir))

    def test_python_package_contents(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, 'a.py')

        name = utils.find_modulename(script, [dirname(python_dir)])
        self.assertEqual("python.a", name)
        name = utils.find_modulename(script, [python_dir])
        self.assertEqual("a", name)
        name = utils.find_modulename(script, [dirname(python_dir), python_dir])
        self.assertEqual("python.a", name)
        #name = utils.find_modulename(script, [python_dir, dirname(python_dir)])
        #self.assertEqual("python.a", name)

    def test_python_script(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, 'a.py')
        self.assert_find_modulename_in_dir("a", script, python_dir)
        self.assert_find_modulename_in_dir("python.a",
            script, dirname(python_dir))

    def test_sys_path(self):
        top = join(dirname(__file__), "..")
        search_path = sys.path[:]
        search_path.insert(0, top)

        self.assertEqual("modipyd", 
            utils.find_modulename(
                join(top, "modipyd/__init__.py"),
                search_path))
        self.assertEqual("modipyd.utils", 
            utils.find_modulename(
                join(top, "modipyd/utils.py"),
                search_path))
        self.assertEqual("modipyd.tools", 
            utils.find_modulename(
                join(top, "modipyd/tools/__init__.py"),
                search_path))

    def test_common_prefix_path(self):
        python_dir = join(FILES_DIR, 'python')
        python2_dir = join(FILES_DIR, 'python2')
        search_path = [python_dir, python2_dir]

        self.assertEqual("b",
            utils.find_modulename(
                join(python2_dir, "b.py"),
                search_path))


if __name__ == '__main__':
    unittest.main()
