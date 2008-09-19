#!/usr/bin/env python

import os
from os.path import abspath, join, dirname
import unittest

from modipyd.pyscript import PyScript
from tests import TestCase


class TestPyScript(TestCase):

    def assert_pyscript(self, script, filepath):
        self.assertNotNone(script)
        self.assertEqual(filepath, script.filename)
        self.assertNotNone(script.mtime)
        self.assertEqual(os.path.getmtime(filepath), script.mtime)

    def test_abspath(self):
        self.assertRaises(RuntimeError, PyScript, 'runtests.py')

    def test_not_found(self):
        filepath = abspath(join(dirname(__file__), 'not_found.py'))
        self.assertRaises(RuntimeError, PyScript, filepath)

    def test_init(self):
        filepath = abspath(join(dirname(__file__), 'test_pyscript.py'))
        self.assert_pyscript(PyScript(filepath), filepath)

    def test_bytecode_file(self):
        """Tests compiled byte-code file"""
        filepath = abspath(__file__)
        pypath = os.path.splitext(filepath)[0] + ".py"
        pycpath = pypath + "c"

        assert pypath.endswith(".py")
        assert pycpath.endswith(".pyc")

        if not os.path.exists(pycpath):
            import py_compile
            print "Compile", pycpath
            py_compile.compile(pypath, pycpath)
            self.assert_(os.path.exists(pycpath))

        self.assert_pyscript(PyScript(pycpath), pycpath)

if __name__ == '__main__':
    unittest.main()
