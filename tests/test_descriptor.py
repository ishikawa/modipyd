#!/usr/bin/env python

import unittest
from modipyd import HAS_RELATIVE_IMPORTS
from os.path import join
from modipyd.descriptor import ModuleDescriptor, \
                               build_module_descriptors
from modipyd.module import collect_module_code, \
                           read_module_code
from tests import TestCase, FILES_DIR


class TestModuleDescriptor(TestCase):

    def test_init(self):
        filepath = join(FILES_DIR, 'python', 'a.py')
        code = read_module_code(filepath, [FILES_DIR])

        self.assertNotNone(code)
        descriptor = ModuleDescriptor(code)

        self.assertEqual('python.a', descriptor.name)
        self.assertEqual(filepath, descriptor.filename)


class TestModuleDescriptorCycleDependency(TestCase):

    def setUp(self):
        codes = list(collect_module_code(
            join(FILES_DIR, 'cycles'),
            [FILES_DIR]))
        self.descriptors = build_module_descriptors(codes)

    def test_dependency(self):
        descriptors = self.descriptors

        # file existence check
        names = set(descriptors.keys())
        names.remove('cycles')
        names.remove('cycles.a')
        names.remove('cycles.b')
        names.remove('cycles.c')
        names.remove('cycles.d')
        names.remove('cycles.e')
        names.remove('cycles.f')
        self.assertEqual(0, len(names))

        # dependency
        a = descriptors['cycles.a']
        self.assertEqual(1, len(a.dependencies))
        self.assertEqual(descriptors['cycles.d'], a.dependencies[0])
        self.assertEqual(1, len(a.reverse_dependencies))
        self.assertEqual(descriptors['cycles.b'], a.reverse_dependencies[0])

    def test_cycles(self):
        descriptors = self.descriptors
        a = descriptors['cycles.a']

        dep = a.walk_dependency_graph(reverse=True)
        self.assertEqual(descriptors['cycles.a'], dep.next())
        self.assertEqual(descriptors['cycles.b'], dep.next())
        self.assertEqual(descriptors['cycles.c'], dep.next())
        self.assertEqual(descriptors['cycles.f'], dep.next())
        self.assertEqual(descriptors['cycles.d'], dep.next())
        self.assertEqual(descriptors['cycles.e'], dep.next())
        self.assertRaises(StopIteration, dep.next)


class TestModuleDescriptorDependency(TestCase):

    def setUp(self):
        codes = list(collect_module_code(
            join(FILES_DIR, 'package_dependency'),
            [FILES_DIR]))
        self.descriptors = build_module_descriptors(codes)
        self.assertEqual(3, len(self.descriptors))

        init = self.descriptors['package_dependency']
        a = self.descriptors['package_dependency.a']
        b = self.descriptors['package_dependency.b']

        self.assertNotNone(init)
        self.assertNotNone(a)
        self.assertNotNone(b)

        self.assertEqual('package_dependency', init.name)
        self.assertEqual('package_dependency.a', a.name)
        self.assertEqual('package_dependency.b', b.name)

    def assert_original_depencencies(self):
        descriptors = self.descriptors
        init = descriptors['package_dependency']
        a = descriptors['package_dependency.a']
        b = descriptors['package_dependency.b']

        self.assertEqual(1, len(init.dependencies))
        self.assertEqual(0, len(init.reverse_dependencies))
        self.assert_(a in init.dependencies)

        self.assertEqual(0, len(a.dependencies))
        self.assertEqual(2, len(a.reverse_dependencies))
        self.assert_(init in a.reverse_dependencies)

        self.assertEqual(1, len(b.dependencies))
        self.assertEqual(0, len(b.reverse_dependencies))
        self.assert_(a in b.dependencies)

    def test_package_dependency(self):
        self.assert_original_depencencies()

    def test_update_dependencies(self):
        descriptors = self.descriptors
        a = descriptors['package_dependency.a']

        self.assert_original_depencencies()
        a.update_dependencies(self.descriptors)
        self.assert_original_depencencies()

    def test_reload(self):
        descriptors = self.descriptors
        init = descriptors['package_dependency']
        a = descriptors['package_dependency.a']
        b = descriptors['package_dependency.b']

        # update with empty code
        co = compile('', '<string>', 'exec')
        b.reload(descriptors, co)

        self.assertEqual(1, len(init.dependencies))
        self.assertEqual(0, len(init.reverse_dependencies))
        self.assert_(a in init.dependencies)

        self.assertEqual(0, len(a.dependencies))
        self.assertEqual(1, len(a.reverse_dependencies))
        self.assert_(init in a.reverse_dependencies)

        self.assertEqual(0, len(b.dependencies))
        self.assertEqual(0, len(b.reverse_dependencies))
        self.assert_(a not in b.dependencies)


class TestModuleDescriptorRelativeImports(TestCase):

    def setUp(self):
        d = join(FILES_DIR, 'imports')
        codes = list(collect_module_code(d, [d]))
        self.descriptors = build_module_descriptors(codes)
        self.assertEqual(8, len(self.descriptors))

    def test_imports(self):
        a = self.descriptors['A.a']
        self.assertEqual(1, len(a.dependencies))
        self.assertEqual(
            self.descriptors['A.B'],
            a.dependencies[0])

    def test_relative_imports(self):
        b = self.descriptors['A.B.b']
        self.assertEqual(1, len(b.dependencies))
        self.assertEqual(
            self.descriptors['A.B.C'],
            b.dependencies[0])

        B = self.descriptors['A.B']
        self.assertEqual(1, len(B.dependencies))
        self.assertEqual(
            self.descriptors['A.B.C'],
            B.dependencies[0])

    def test_relative_imports_level(self):
        c = self.descriptors['A.B.C.c']
        self.assertEqual(2, len(c.dependencies))
        self.assertEqual(
            self.descriptors['A.B.C'],
            c.dependencies[0])
        self.assertEqual(
            self.descriptors['A.B.D'],
            c.dependencies[1])


if not HAS_RELATIVE_IMPORTS:
    del TestModuleDescriptorRelativeImports

if __name__ == '__main__':
    unittest.main()
