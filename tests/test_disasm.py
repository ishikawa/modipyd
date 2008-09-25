#!/usr/bin/env python

import unittest
from modipyd.disasm import ImportDisassembler
from tests import TestCase


class TestModipydImportDisassembler(TestCase):

    def compile(self, src):
        return compile(src, '<string>', 'exec')

    def compile_scan(self, src):
        co = self.compile(src)
        disasm = ImportDisassembler(co)
        self.assertNotNone(disasm)
        return disasm.scan()

    def test_simple(self):
        imports = self.compile_scan("import os")
        self.assertEqual(1, len(imports))
        self.assertEqual(3, len(imports[0]))
        self.assertEqual('os', imports[0][0])
        self.assertEqual('os', imports[0][1])
        self.assertEqual(-1, imports[0][2])

    def test_submodule(self):
        imports = self.compile_scan("import os.path")
        self.assertEqual(1, len(imports))
        self.assertEqual('os.path', imports[0][0])
        self.assertEqual('os.path', imports[0][1])
        self.assertEqual(-1, imports[0][2])

        imports = self.compile_scan("import os.path as os_path")
        self.assertEqual(1, len(imports))
        self.assertEqual('os_path', imports[0][0])
        self.assertEqual('os.path', imports[0][1])
        self.assertEqual(-1, imports[0][2])

    def test_multiple(self):
        imports = self.compile_scan("import os, sys as sys_mod")
        self.assertEqual(2, len(imports))
        self.assertEqual('os', imports[0][0])
        self.assertEqual('os', imports[0][1])
        self.assertEqual(-1, imports[0][2])
        self.assertEqual('sys_mod', imports[1][0])
        self.assertEqual('sys', imports[1][1])
        self.assertEqual(-1, imports[1][2])

    def test_fromlist(self):
        imports = self.compile_scan("from os import path")
        self.assertEqual(1, len(imports))
        self.assertEqual('path', imports[0][0])
        self.assertEqual('os.path', imports[0][1])
        self.assertEqual(-1, imports[0][2])

        imports = self.compile_scan("from os.path import join")
        self.assertEqual(1, len(imports))
        self.assertEqual('join', imports[0][0])
        self.assertEqual('os.path.join', imports[0][1])
        self.assertEqual(-1, imports[0][2])

        imports = self.compile_scan("from os.path import dirname, join")
        self.assertEqual(2, len(imports))
        self.assertEqual('dirname', imports[0][0])
        self.assertEqual('os.path.dirname', imports[0][1])
        self.assertEqual('join', imports[1][0])
        self.assertEqual('os.path.join', imports[1][1])
        self.assertEqual(-1, imports[0][2])

        imports = self.compile_scan("from os.path import dirname as d, join")
        self.assertEqual(2, len(imports))
        self.assertEqual('d', imports[0][0])
        self.assertEqual('os.path.dirname', imports[0][1])
        self.assertEqual(-1, imports[0][2])
        self.assertEqual('join', imports[1][0])
        self.assertEqual('os.path.join', imports[1][1])
        self.assertEqual(-1, imports[1][2])

    def test_star(self):
        imports = self.compile_scan("from os.path import *")
        # from ... import * is currently not fully supported
        self.assertEqual(1, len(imports))
        self.assertEqual('*', imports[0][0])
        self.assertEqual('os.path.*', imports[0][1])
        self.assertEqual(-1, imports[0][2])

    def test_relative_import_with_modulename(self):
        imports = self.compile_scan("from . A import B")
        self.assertEqual(1, len(imports))
        self.assertEqual('B', imports[0][0])
        self.assertEqual('A.B', imports[0][1])
        self.assertEqual(1, imports[0][2])

        imports = self.compile_scan("from .. A import B")
        self.assertEqual(1, len(imports))
        self.assertEqual('B', imports[0][0])
        self.assertEqual('A.B', imports[0][1])
        self.assertEqual(2, imports[0][2])

    def test_relative_import_without_modulename(self):
        imports = self.compile_scan("from . import A")
        self.assertEqual(1, len(imports))
        self.assertEqual('A', imports[0][0])
        self.assertEqual('A', imports[0][1])
        self.assertEqual(1, imports[0][2])

        imports = self.compile_scan("from .. import A")
        self.assertEqual(1, len(imports))
        self.assertEqual('A', imports[0][0])
        self.assertEqual('A', imports[0][1])
        self.assertEqual(2, imports[0][2])

    def test_future(self):
        imports = self.compile_scan("from __future__ import absolute_import")
        self.assertEqual(1, len(imports))
        self.assertEqual('absolute_import', imports[0][0])
        self.assertEqual('__future__.absolute_import', imports[0][1])
        self.assertEqual(0, imports[0][2])


if __name__ == '__main__':
    unittest.main()
