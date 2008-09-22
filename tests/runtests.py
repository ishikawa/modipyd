#! /usr/bin/env python

"""
Regression tests for modipyd
"""

import os
import unittest
from os.path import join, dirname
from modipyd.utils import resolve_modulename, import_module

tests = unittest.TestSuite()

for dirpath, dirnames, filenames in os.walk(dirname(__file__)):
    for name in filenames:
        if not (name.startswith("test_") and name.endswith(".py")):
            continue

        filepath = join(dirpath, name)
        modulename = resolve_modulename(filepath)
        module = import_module(modulename)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        tests.addTest(suite)

if __name__ == '__main__':
    unittest.TextTestRunner().run(tests)
