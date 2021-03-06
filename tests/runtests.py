#! /usr/bin/env python

"""
Regression tests for modipyd
"""

import os
import sys
import unittest
import doctest
from os.path import join, dirname

# Bacause the installed Modipyd in site_packages directory is found
# earlier than PYTHONPATH, I need to modify sys.path manually.
sys.path.insert(0, join(dirname(__file__), '..'))

from modipyd.utils import resolve_modulename, import_module
from modipyd.module import collect_module_code


def gather_tests():
    """Returns unittest.TestSuite instance"""
    tests = unittest.TestSuite()

    # unittest
    for dirpath, dirnames, filenames in os.walk(dirname(__file__)):
        if 'files' in dirnames:
            dirnames.remove('files')

        for name in filenames:
            if not (name.startswith("test_") and name.endswith(".py")):
                continue

            filepath = join(dirpath, name)
            modulename = resolve_modulename(filepath)
            module = import_module(modulename)
            suite = unittest.defaultTestLoader.loadTestsFromModule(module)
            tests.addTest(suite)

    # doctest
    modipyd_dir = join(dirname(__file__), '..', 'modipyd')
    for modcode in collect_module_code(modipyd_dir):
        module = import_module(modcode.name)
        try:
            suite = doctest.DocTestSuite(module)
        except ValueError:
            pass
        else:
            tests.addTest(suite)

    return tests


if __name__ == '__main__':
    unittest.TextTestRunner().run(gather_tests())
