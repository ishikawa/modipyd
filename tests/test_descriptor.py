#!/usr/bin/env python

import unittest
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
        self.assertEqual(filepath, descriptor.filepath)


class TestModuleDescriptorDependency(TestCase):

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


if __name__ == '__main__':
    unittest.main()
