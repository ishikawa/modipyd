#! /usr/bin/env python

"""
Regression tests for modipyd
"""

import os
import unittest
import imp
from os.path import join, dirname, basename, splitext
from modipyd.utils import detect_modulename

tests = unittest.TestSuite()

#import sys, pprint
#pprint.pprint(sys.path)

for dirpath, dirnames, filenames in os.walk(dirname(__file__)):
    for name in filenames:
        if not (name.startswith("test_") and name.endswith(".py")):
            continue

        filepath = join(dirpath, name)
        modulename = detect_modulename(filepath)
        #print modulename
        module = imp.load_source(modulename, filepath)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        tests.addTest(suite)

if __name__ == '__main__':
    unittest.TextTestRunner().run(tests)
