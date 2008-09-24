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

        module = ModuleCode('a', py, code)
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
        self.assertEqual(filepath, module.filepath)
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

    def test_imports_classdefs(self):
        modcode = self.read_module_code('module_code.imports_classdefs')
        self.assertEqual(2, len(modcode.imports))

if __name__ == '__main__':
    unittest.main()
