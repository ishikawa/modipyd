#! /usr/bin/env python

"""
Regression tests for modipyd
"""

import os
import unittest
import doctest
from os.path import join, dirname

from modipyd.utils import resolve_modulename, import_module
from modipyd.module import collect_module_code


tests = unittest.TestSuite()

# unittest
for dirpath, dirnames, filenames in os.walk(dirname(__file__)):
    for name in filenames:
        if not (name.startswith("test_") and name.endswith(".py")):
            continue

        filepath = join(dirpath, name)
        modulename = resolve_modulename(filepath)
        module = import_module(modulename)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        tests.addTest(suite)

# doctest
for modcode in collect_module_code(join(dirname(__file__), '..', 'modipyd')):
    module = import_module(modcode.name)
    tests.addTest(doctest.DocTestSuite(module))


if __name__ == '__main__':
    unittest.TextTestRunner().run(tests)
