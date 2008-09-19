#!/usr/bin/env python

import re
import unittest
import os
from os.path import join

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
        self.assertRaises(RuntimeError, utils.detect_modulename, None)
        self.assertRaises(RuntimeError, utils.detect_modulename, "")


class TestMakeModulename(TestCase):

    MODULE_NAME_RE = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*$')

    def assert_modulename(self, s):
        r = TestMakeModulename.MODULE_NAME_RE
        self.assert_(r.match(utils.make_modulename(s)))

    def assert_different_modulename(self, s1, s2):
        modname1 = utils.make_modulename(s1)
        modname2 = utils.make_modulename(s2)
        self.assertNotEqual(modname1, modname2)

    def test_make_modulename(self):
        self.assert_modulename("")
        self.assert_modulename("A")
        self.assert_modulename("/")
        self.assert_modulename("/usr/bin/python")
        self.assert_modulename("/usr/bin/test.py")

    def test_different_modulename(self):
        self.assert_different_modulename("", "A")
        self.assert_different_modulename("/path/to/test.py", "/path/to/test")
        self.assert_different_modulename(
            "/path/to/test@!?.py", "/path/to/test@!!.py")


if __name__ == '__main__':
    unittest.main()
