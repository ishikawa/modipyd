#! /usr/bin/env python

"""
Regression tests for modipyd
"""

import os
import sys
import unittest
import imp
from os.path import join, normpath, dirname

sys.path.insert(0, join(dirname(__file__), '..'))
from modipyd import make_modulename


tests = unittest.TestSuite()

for dirpath, dirnames, filenames in os.walk(dirname(__file__)):
    for name in filenames:
        if not (name.startswith("test_") and name.endswith(".py")):
            continue
        filepath = join(dirpath, name)
        module = imp.load_source(make_modulename(filepath), filepath)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        tests.addTest(suite)
        #print "Found:", filepath


if __name__ == '__main__':
    unittest.TextTestRunner().run(tests)
