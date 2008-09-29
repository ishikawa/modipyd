#!/usr/bin/env python

import unittest
from modipyd import bytecode as bc
from modipyd import HAS_RELATIVE_IMPORTS
from tests import TestCase


class DisassemblerTestCase(TestCase):

    def compile(self, src, filename='<string>'):
        return compile(src, filename, 'exec')

    def compile_scan_imports(self, src, filename='<string>'):
        co = self.compile(src, filename)
        context = {}
        processor = bc.ImportProcessor()
        self.assertNotNone(processor)
        bc.scan_code(co, processor, context)
        return context['imports']


class TestDisassembler25(DisassemblerTestCase):

    def test_relative_import_with_modulename(self):
        imports = self.compile_scan_imports("from . A import B")
        self.assertEqual(1, len(imports))
        self.assertEqual('B', imports[0][0])
        self.assertEqual('A.B', imports[0][1])
        self.assertEqual(1, imports[0][2])

        imports = self.compile_scan_imports("from .. A import B")
        self.assertEqual(1, len(imports))
        self.assertEqual('B', imports[0][0])
        self.assertEqual('A.B', imports[0][1])
        self.assertEqual(2, imports[0][2])

    def test_relative_import_without_modulename(self):
        imports = self.compile_scan_imports("from . import A")
        self.assertEqual(1, len(imports))
        self.assertEqual('A', imports[0][0])
        self.assertEqual('A', imports[0][1])
        self.assertEqual(1, imports[0][2])

        imports = self.compile_scan_imports("from .. import A")
        self.assertEqual(1, len(imports))
        self.assertEqual('A', imports[0][0])
        self.assertEqual('A', imports[0][1])
        self.assertEqual(2, imports[0][2])

    def test_relative_import_without_modulename_as(self):
        imports = self.compile_scan_imports("from .. import A as b")
        self.assertEqual(1, len(imports))
        self.assertEqual('b', imports[0][0])
        self.assertEqual('A', imports[0][1])
        self.assertEqual(2, imports[0][2])

    def test_future(self):
        imports = self.compile_scan_imports(
            "from __future__ import absolute_import")
        self.assertEqual(1, len(imports))
        self.assertEqual('absolute_import', imports[0][0])
        self.assertEqual('__future__.absolute_import', imports[0][1])
        self.assertEqual(0, imports[0][2])


class TestDisassembler(DisassemblerTestCase):

    def test_simple(self):
        imports = self.compile_scan_imports("import os")
        self.assertEqual(1, len(imports))
        self.assertEqual(3, len(imports[0]))
        self.assertEqual('os', imports[0][0])
        self.assertEqual('os', imports[0][1])
        self.assertEqual(-1, imports[0][2])

    def test_submodule(self):
        imports = self.compile_scan_imports("import os.path")
        self.assertEqual(1, len(imports))
        self.assertEqual('os.path', imports[0][0])
        self.assertEqual('os.path', imports[0][1])
        self.assertEqual(-1, imports[0][2])

        imports = self.compile_scan_imports("import os.path as os_path")
        self.assertEqual(1, len(imports))
        self.assertEqual('os_path', imports[0][0])
        self.assertEqual('os.path', imports[0][1])
        self.assertEqual(-1, imports[0][2])

    def test_local_scope(self):
        imports = self.compile_scan_imports("""
def import_module():
    import os.path""", "<test_local_scope>")
        self.assertEqual(1, len(imports))
        self.assertEqual('os.path', imports[0][0])
        self.assertEqual('os.path', imports[0][1])
        self.assertEqual(-1, imports[0][2])

    def test_bind_scope(self):
        imports = self.compile_scan_imports("""
def fn():
    import fnmatch
    def ignore(filename):
        if fnmatch.fnmatch(filename, '*'):
            pass
""", "<test_local_scope>")
        self.assertEqual(1, len(imports))
        self.assertEqual('fnmatch', imports[0][0])
        self.assertEqual('fnmatch', imports[0][1])
        self.assertEqual(-1, imports[0][2])

    def test_multiple(self):
        imports = self.compile_scan_imports("import os, sys as sys_mod")
        self.assertEqual(2, len(imports))
        self.assertEqual('os', imports[0][0])
        self.assertEqual('os', imports[0][1])
        self.assertEqual(-1, imports[0][2])
        self.assertEqual('sys_mod', imports[1][0])
        self.assertEqual('sys', imports[1][1])
        self.assertEqual(-1, imports[1][2])

    def test_fromlist(self):
        imports = self.compile_scan_imports("from os import path")
        self.assertEqual(1, len(imports))
        self.assertEqual('path', imports[0][0])
        self.assertEqual('os.path', imports[0][1])
        self.assertEqual(-1, imports[0][2])

        imports = self.compile_scan_imports("from os.path import join")
        self.assertEqual(1, len(imports))
        self.assertEqual('join', imports[0][0])
        self.assertEqual('os.path.join', imports[0][1])
        self.assertEqual(-1, imports[0][2])

        imports = self.compile_scan_imports("from os.path import dirname, join")
        self.assertEqual(2, len(imports))
        self.assertEqual('dirname', imports[0][0])
        self.assertEqual('os.path.dirname', imports[0][1])
        self.assertEqual('join', imports[1][0])
        self.assertEqual('os.path.join', imports[1][1])
        self.assertEqual(-1, imports[0][2])

        imports = self.compile_scan_imports(
            "from os.path import dirname as d, join")
        self.assertEqual(2, len(imports))
        self.assertEqual('d', imports[0][0])
        self.assertEqual('os.path.dirname', imports[0][1])
        self.assertEqual(-1, imports[0][2])
        self.assertEqual('join', imports[1][0])
        self.assertEqual('os.path.join', imports[1][1])
        self.assertEqual(-1, imports[1][2])

    def test_star(self):
        imports = self.compile_scan_imports("from os.path import *")
        # from ... import * is currently not fully supported
        self.assertEqual(1, len(imports))
        self.assertEqual('*', imports[0][0])
        self.assertEqual('os.path.*', imports[0][1])
        self.assertEqual(-1, imports[0][2])

    def test_django_contrib_gis_tests_test_gdal_geom(self):
        imports = self.compile_scan_imports("""
from django.contrib.gis.tests.geometries import *
class OGRGeomTest(unittest.TestCase):
    pass
""")
        # from ... import * is currently not fully supported
        self.assertEqual(1, len(imports))
        self.assertEqual('*', imports[0][0])
        self.assertEqual('django.contrib.gis.tests.geometries.*', imports[0][1])
        self.assertEqual(-1, imports[0][2])


if not HAS_RELATIVE_IMPORTS:
    del TestDisassembler25

if __name__ == '__main__':
    unittest.main()
