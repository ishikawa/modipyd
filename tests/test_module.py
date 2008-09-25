#!/usr/bin/env python

import unittest
from os.path import join
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
        self.assertEqual(0, len(module.imports))

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
        module = read_module_code(filepath, [FILES_DIR])

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
        self.assertEqual(5, len(modcode.imports))

        # import sys
        self.assertEqual(('sys', 'sys', -1), modcode.imports[0])
        self.assertEqual(('join', 'os.path.join', -1), modcode.imports[1])
        self.assertEqual(('dirname', 'os.path.dirname', -1),
            modcode.imports[2])
        self.assertEqual(('unittest', 'unittest', -1), modcode.imports[3])
        self.assertEqual(('altos', 'os', -1), modcode.imports[4])

    def test_classdefs(self):
        modcode = self.read_module_code('module_code.imports_classdefs')
        self.assertEqual(4, len(modcode.classdefs))

        # class A:
        self.assertEqual('A', modcode.classdefs[0][0])
        self.assertEqual(0, len(modcode.classdefs[0][1]))

        # class B(object):
        self.assertEqual('B', modcode.classdefs[1][0])
        self.assertEqual(1, len(modcode.classdefs[1][1]))
        self.assertEqual('object', modcode.classdefs[1][1][0])

        # class C(unittest.TestCase):
        self.assertEqual('C', modcode.classdefs[2][0])
        self.assertEqual(1, len(modcode.classdefs[2][1]))
        self.assertEqual('unittest.TestCase', modcode.classdefs[2][1][0])

        # class D(A, C):
        self.assertEqual('D', modcode.classdefs[3][0])
        self.assertEqual(2, len(modcode.classdefs[3][1]))
        self.assertEqual('A', modcode.classdefs[3][1][0])


if __name__ == '__main__':
    unittest.main()
