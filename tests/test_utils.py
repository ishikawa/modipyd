#!/usr/bin/env python

import unittest
import os
import sys
from os.path import basename, join, normpath, \
                    dirname, exists, isdir
from errno import ENOENT

from modipyd import utils, resolve
from tests import TestCase, FILES_DIR
from modipyd.resolve import script_filename_to_modulename


def _modname(filepath):
    return script_filename_to_modulename(resolve.normalize_path(filepath))


class TestModipydUtils(TestCase):

    def test_wrap_sequence(self):
        self.assertEqual([], utils.wrap_sequence([]))
        self.assertEqual([1, 2, 3], utils.wrap_sequence([1, 2, 3]))
        self.assertEqual((1,), utils.wrap_sequence(1))
        self.assertEqual([1], utils.wrap_sequence(1, list))


class TestModipydCollectFiles(TestCase):
    """Tests modipyd functionalities"""

    def test_files_dir_exists(self):
        self.assert_(exists(FILES_DIR))
        self.assert_(isdir(FILES_DIR))

    def test_not_found(self):
        filename = join(FILES_DIR, 'no file or directory')
        self.assert_(not exists(filename))

        try:
            list(utils.collect_files(filename))
        except IOError, ioe:
            self.assertEqual(ENOENT, ioe.errno)
            self.assertEqual(filename, ioe.filename)
        else:
            self.fail("Expected IOError")

    def empty_directory(self):
        directory = join(FILES_DIR, 'empty')
        if not exists(directory):
            os.mkdir(directory)
        self.assert_(exists(directory))
        self.assert_(isdir(directory))
        return directory

    def test_empty_directory(self):
        directory = self.empty_directory()
        files = list(utils.collect_files(directory))
        self.assertNotNone(files)
        self.assertEqual(0, len(files))

    def test_files(self):
        directory = join(FILES_DIR, '000')
        files = list(utils.collect_files(directory))
        self.assertNotNone(files)
        self.assertEqual(6, len(files))

        files[:] = [normpath(f) for f in files]
        self.assert_(directory not in files)
        for f in ['001', '002', '003', '004/A', '004/B', '004/C']:
            f = normpath(join(directory, f))
            self.assert_(f in files)

    def test_ignore_pattern(self):
        directory = join(FILES_DIR, '000')
        files = list(utils.collect_files(directory, ['004']))
        self.assertNotNone(files)
        self.assertEqual(3, len(files))

        files[:] = [normpath(f) for f in files]
        self.assert_(directory not in files)
        for f in ['001', '002', '003']:
            f = normpath(join(directory, f))
            self.assert_(f in files)

    def test_multiple_ignore_directories(self):
        directory = join(FILES_DIR, 'imports')
        files = list(utils.collect_files(directory, ['C', 'D']))

        self.assertNotNone(files)
        self.assertNotEqual(0, len(files))

        scripts = sorted([basename(x) for x in files if x.endswith('.py')])
        self.assertEqual(4, len(scripts))
        self.assertEqual('__init__.py', scripts[0])
        self.assertEqual('__init__.py', scripts[1])
        self.assertEqual('a.py', scripts[2])
        self.assertEqual('b.py', scripts[3])


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


class TestRelativePath(TestCase):

    def test_empty(self):
        self.assertRaises(TypeError, utils.relativepath, None)
        self.assertEqual("", utils.relativepath(""))


class TestResolveModulename(TestCase):

    def test_empty(self):
        self.assertRaises(ImportError, utils.resolve_modulename, None)
        self.assertRaises(ImportError, utils.resolve_modulename, "")

    def assert_resolve_modulename_in_dir(self,
                            expected_name, filepath, directory):
        name = utils.resolve_modulename(filepath, [directory])
        self.assertEqual(expected_name,
            name,
            "Expected module name is '%s', but was '%s' (%s in %s)" %
            (expected_name, name, filepath, directory))

        # '/'
        directory += '/'
        name = utils.resolve_modulename(filepath, [directory])
        self.assertEqual(expected_name,
            name,
            "Expected module name is '%s', but was '%s' (%s in %s)" %
            (expected_name, name, filepath, directory))

    def test_package_init_module(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, '__init__.py')
        self.assert_resolve_modulename_in_dir("python",
            script, dirname(python_dir))

    def test_package(self):
        self.assert_resolve_modulename_in_dir('python.a',
            join(FILES_DIR, 'python/a.py'), FILES_DIR)
        self.assert_resolve_modulename_in_dir('python2.b',
            join(FILES_DIR, 'python2/b.py'), FILES_DIR)

        # not a package
        filepath = join(FILES_DIR, 'python3/c.py')
        name = utils.resolve_modulename(filepath, [join(FILES_DIR, 'python3')])
        self.assertEqual(_modname(filepath), name)

        self.assertRaises(
            ImportError,
            utils.resolve_modulename,
            join(FILES_DIR, 'python3/c.py'),
            [FILES_DIR])

    def test_search_package(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, 'a.py')

        name = utils.resolve_modulename(
            script, [dirname(python_dir)])
        self.assertEqual("python.a", name)
        name = utils.resolve_modulename(script, [python_dir])
        self.assertEqual(_modname(script), name)
        name = utils.resolve_modulename(
            script, [dirname(python_dir), python_dir])
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

        name = utils.resolve_modulename(script, search_path)
        self.assertEqual('python.a', name)

    def test_package_in_not_package(self):
        search_path = [join(dirname(__file__), '..')]
        script = join(FILES_DIR, 'python', 'a.py')
        self.assertRaises(ImportError,
            utils.resolve_modulename, script, search_path)

    def test_python_script(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, 'a.py')
        self.assert_resolve_modulename_in_dir(_modname(script), script, python_dir)
        self.assert_resolve_modulename_in_dir("python.a",
            script, dirname(python_dir))

    def test_not_in_search_path(self):
        python_dir = join(FILES_DIR, 'python')
        script = join(python_dir, 'a.py')
        self.assertRaises(ImportError, utils.resolve_modulename, script, [])

    def test_sys_path(self):
        top = join(dirname(__file__), "..")
        search_path = sys.path[:]
        search_path.insert(0, top)

        self.assertEqual("modipyd", 
            utils.resolve_modulename(
                join(top, "modipyd/__init__.py"),
                search_path))
        self.assertEqual("modipyd.utils", 
            utils.resolve_modulename(
                join(top, "modipyd/utils/__init__.py"),
                search_path))
        self.assertEqual("modipyd.tools", 
            utils.resolve_modulename(
                join(top, "modipyd/tools/__init__.py"),
                search_path))

    def test_common_prefix_path(self):
        python_dir = join(FILES_DIR, 'python')
        python2_dir = join(FILES_DIR, 'python2')
        search_path = [python_dir, python2_dir]

        filepath = join(python2_dir, "b.py")
        self.assertEqual(
            _modname(filepath),
            utils.resolve_modulename(filepath, search_path))


if __name__ == '__main__':
    unittest.main()
