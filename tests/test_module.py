#!/usr/bin/env python

import unittest
from os.path import abspath, join, exists
from modipyd.utils import compile_python_source
from modipyd.module import ModuleCode, compile_source, \
                           collect_module_code, \
                           read_module_code
from tests import TestCase, FILES_DIR


class TestModipydModuleCode(TestCase):

    def test_init(self):
        py = join(FILES_DIR, 'python', 'a.py')
        code = compile_source(py)
        self.assertNotNone(code)

        module = ModuleCode('a', None, py, code)
        self.assertNotNone(module)
        self.assertEqual(0, len(module.context['imports']))

    def test_collect_module_code(self):
        modules = list(collect_module_code(
            join(FILES_DIR, 'python'),
            [FILES_DIR]))
        self.assertNotNone(modules)
        self.assertEqual(2, len(modules))

        names = [m.name for m in modules]
        self.assert_('python.a' in names)
        self.assert_('python' in names)

    def read_module_code(self, modulename):
        items = [FILES_DIR] + list(modulename.split('.'))
        items[-1] += '.py'
        filepath = join(*items)
        module = read_module_code(filepath, search_path=[FILES_DIR])

        self.assertNotNone(module)
        self.assertEqual(modulename, module.name)
        self.assertEqual(filepath, module.filename)
        return module

    def test_python_module(self):
        self.read_module_code('python.a')

    def test_module_equality(self):
        modules = list(collect_module_code(
            join(FILES_DIR, 'python'),
            [FILES_DIR]))
        self.assertEqual(2, len(modules))

        module1 = modules[0]
        module2 = modules[1]

        self.assert_(module1 is not module2)
        self.assert_(not module1 == module2)
        self.assert_(module1 is module1)
        self.assert_(module1 == module1)

        modules2 = list(collect_module_code(
            join(FILES_DIR, 'python'),
            [FILES_DIR]))

        self.assert_(module1 is not modules2[0])
        self.assert_(module1 == modules2[0])

        # hash
        self.assertEqual(hash(module1), hash(module1))
        self.assertEqual(hash(module1), hash(modules2[0]))
        self.assertEqual(hash(module2), hash(modules2[1]))

    def test_read_module_code_not_existense(self):
        # Can't import a module in no package
        self.assertRaises(ImportError, self.read_module_code, 'python3.c')

    def test_imports(self):
        modcode = self.read_module_code('module_code.imports_classdefs')
        imports = modcode.context['imports']
        self.assertEqual(5, len(imports))

        # import sys
        self.assertEqual(('sys', 'sys', -1), imports[0])
        self.assertEqual(('join', 'os.path.join', -1), imports[1])
        self.assertEqual(('dirname', 'os.path.dirname', -1), imports[2])
        self.assertEqual(('unittest', 'unittest', -1), imports[3])
        self.assertEqual(('altos', 'os', -1), imports[4])

    def test_classdefs(self):
        modcode = self.read_module_code('module_code.imports_classdefs')
        classdefs = modcode.context['classdefs']
        self.assertEqual(4, len(classdefs))

        # class A:
        self.assertEqual('A', classdefs[0][0])
        self.assertEqual(0, len(classdefs[0][1]))

        # class B(object):
        self.assertEqual('B', classdefs[1][0])
        self.assertEqual(1, len(classdefs[1][1]))
        self.assertEqual('object', classdefs[1][1][0])

        # class C(unittest.TestCase):
        self.assertEqual('C', classdefs[2][0])
        self.assertEqual(1, len(classdefs[2][1]))
        self.assertEqual('unittest.TestCase', classdefs[2][1][0])

        # class D(A, C):
        self.assertEqual('D', classdefs[3][0])
        self.assertEqual(2, len(classdefs[3][1]))
        self.assertEqual('A', classdefs[3][1][0])

    def test_python_module_reload(self):
        search_path = abspath(join(FILES_DIR, 'imports'))
        pypath = abspath(join(search_path, 'A', 'a.py'))
        assert exists(pypath)

        pycpath = abspath(join(search_path, 'A', 'a.pyc'))
        pyopath = abspath(join(search_path, 'A', 'a.pyo'))
        if not exists(pycpath) or not exists(pyopath):
            compile_python_source(pypath)
            compile_python_source(pypath, optimization=True)
        assert exists(pycpath) and exists(pyopath)

        m = read_module_code(pypath, search_path=[search_path])
        old_imports = m.context['imports'][:]
        old_classdefs = m.context['classdefs'][:]

        for f in [pypath, pycpath, pyopath]:
            # ugly ...
            del m.context['imports'][:]
            del m.context['classdefs'][:]
            m.filename = f

            co = m.reload()
            self.assertNotNone(co)
            self.assertEqual(pypath, co.co_filename)
            self.assertEqual(old_imports, m.context['imports'])
            self.assertEqual(old_classdefs, m.context['classdefs'])


if __name__ == '__main__':
    unittest.main()
