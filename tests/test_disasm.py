#!/usr/bin/env python

import unittest
from modipyd.module import ImportDisasm
from tests import TestCase


class TestModipydImportDisasm(TestCase):

    def compile(self, src):
        return compile(src, '<string>', 'exec')

    def compile_scan(self, src):
        co = self.compile(src)
        disasm = ImportDisasm(co)
        self.assertNotNone(disasm)
        return disasm.scan()

    def test_simple(self):
        imports = self.compile_scan("import os")
        self.assertEqual(1, len(imports))
        self.assertEqual(2, len(imports[0]))
        self.assertEqual('os', imports[0][0])
        self.assertEqual('os', imports[0][1])

    def test_submodule(self):
        imports = self.compile_scan("import os.path")
        self.assertEqual(1, len(imports))
        self.assertEqual('os.path', imports[0][0])
        self.assertEqual('os.path', imports[0][1])

        imports = self.compile_scan("import os.path as os_path")
        self.assertEqual(1, len(imports))
        self.assertEqual('os_path', imports[0][0])
        self.assertEqual('os.path', imports[0][1])

    def test_multiple(self):
        imports = self.compile_scan("import os, sys as sys_mod")
        self.assertEqual(2, len(imports))
        self.assertEqual('os', imports[0][0])
        self.assertEqual('os', imports[0][1])
        self.assertEqual('sys_mod', imports[1][0])
        self.assertEqual('sys', imports[1][1])

    def test_fromlist(self):
        imports = self.compile_scan("from os import path")
        self.assertEqual(1, len(imports))
        self.assertEqual('path', imports[0][0])
        self.assertEqual('os.path', imports[0][1])


if __name__ == '__main__':
    unittest.main()
