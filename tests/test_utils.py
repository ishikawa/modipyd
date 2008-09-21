#!/usr/bin/env python

import unittest
import sys
from os.path import join, dirname, exists

from modipyd import utils
from tests import TestCase, FILES_DIR


class TestModipydUtils(TestCase):

    def test_wrap_sequence(self):
        self.assertEqual([], utils.wrap_sequence([]))
        self.assertEqual([1, 2, 3], utils.wrap_sequence([1, 2, 3]))
        self.assertEqual((1,), utils.wrap_sequence(1))
        self.assertEqual([1], utils.wrap_sequence(1, list))


class TestModipyPathUtils(TestCase):

    def setUp(self):
        self.notpypath = join(FILES_DIR, '000', '001')
        self.pypath  = join(FILES_DIR, 'python', 'a.py')
        self.pycpath = join(FILES_DIR, 'python', 'a.pyc')
        self.pyopath = join(FILES_DIR, 'python', 'a.pyo')

        assert exists(self.pypath)
        if not exists(self.pycpath) or not exists(self.pyopath):
            utils.compile_python_source(self.pypath)
            utils.compile_python_source(self.pypath, optimization=True)
        assert exists(self.pycpath)
        assert exists(self.pyopath)

    def test_python_module_file(self):
        self.assert_(utils.python_module_file(self.pypath))
        self.assert_(utils.python_module_file(self.pycpath))
        self.assert_(utils.python_module_file(self.pyopath))
        self.assert_(not utils.python_module_file(self.notpypath))

    def test_python_module_file2(self):
        filepath = join(FILES_DIR, '000/001')
        script = join(FILES_DIR, 'python/a.py')

        assert exists(filepath)
        assert exists(script)

        self.assert_(not utils.python_module_file(None))
        self.assert_(not utils.python_module_file(""))

        self.assert_(utils.python_module_file(script),
            "Expected python file: %s" % script)
        self.assert_(not utils.python_module_file(filepath),
            "Expected not python file: %s" % filepath)
        self.assert_(not utils.python_module_file("not_found_file"))

    def test_python_module_exists(self):
        python_dir = join(FILES_DIR, 'python')
        self.assert_(utils.python_module_exists(python_dir, 'a'))
        self.assert_(utils.python_module_exists(python_dir, '__init__'))
        self.assert_(not utils.python_module_exists(python_dir, 'unknown'))

    def test_python_package(self):
        self.assert_(utils.python_package(join(FILES_DIR, 'python')))
        self.assert_(not utils.python_package(FILES_DIR))


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

    def test_package_init_module(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, '__init__.py')
        self.assert_find_modulename_in_dir("python",
            script, dirname(python_dir))

    def test_package(self):
        self.assert_find_modulename_in_dir('python.a',
            join(FILES_DIR, 'python/a.py'), FILES_DIR)
        self.assert_find_modulename_in_dir('python2.b',
            join(FILES_DIR, 'python2/b.py'), FILES_DIR)

        # not a package
        name = utils.find_modulename(
            join(FILES_DIR, 'python3/c.py'),
            [join(FILES_DIR, 'python3')])
        self.assertEqual('c', name)

        self.assertRaises(
            ImportError,
            utils.find_modulename,
            join(FILES_DIR, 'python3/c.py'),
            [FILES_DIR])

    def test_search_package(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, 'a.py')

        name = utils.find_modulename(script, [dirname(python_dir)])
        self.assertEqual("python.a", name)
        name = utils.find_modulename(script, [python_dir])
        self.assertEqual("a", name)
        name = utils.find_modulename(script, [dirname(python_dir), python_dir])
        self.assertEqual("python.a", name)

    def test_search_package_priority(self):
        """
        Consider:

            src/packageA/__init__.py
                        /a.py

        and *sys.path* is:

            ['src/packageA', 'src']

        a.py is in src/packageA, so module name 'a' is matched.
        But better module name is 'packageA.a' because a.py is
        created under the package 'packageA'.
        """
        search_path = [join(FILES_DIR, 'python'), FILES_DIR]
        script = join(FILES_DIR, 'python', 'a.py')

        name = utils.find_modulename(script, search_path)
        #self.assertEqual('python.a', name)


    def test_python_script(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, 'a.py')
        self.assert_find_modulename_in_dir("a", script, python_dir)
        self.assert_find_modulename_in_dir("python.a",
            script, dirname(python_dir))

    def test_not_in_search_path(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, 'a.py')
        self.assertRaises(ImportError, utils.find_modulename, script, [])

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
