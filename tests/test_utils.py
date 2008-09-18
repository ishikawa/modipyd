#!/usr/bin/env python

import re
import unittest
import unittest_helper
import modipyd
from modipyd import utils


class TestModipydUtils(unittest_helper.TestCase):

    def test_wrap_sequence(self):
        self.assertEqual([], utils.wrap_sequence([]))
        self.assertEqual([1, 2, 3], utils.wrap_sequence([1, 2, 3]))
        self.assertEqual((1,), utils.wrap_sequence(1))
        self.assertEqual([1], utils.wrap_sequence(1, list))


class TestMakeModulename(unittest_helper.TestCase):

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
        self.assert_different_modulename("/path/to/test@!?.py", "/path/to/test@!!.py")


if __name__ == '__main__':
    unittest.main()
