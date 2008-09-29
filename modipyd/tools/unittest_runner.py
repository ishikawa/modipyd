"""
A command-line program that runs a set of tests; this is primarily for making
test modules conveniently executable.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import sys
import unittest

from modipyd import LOGGER, utils


def collect_unittest(module_names):
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for name in module_names:
        try:
            module = utils.import_module(name)
        except ImportError:
            LOGGER.warn(
                "ImportError occurred while loading module",
                exc_info=True)
        else:
            tests = loader.loadTestsFromModule(module)
            if tests.countTestCases():
                suite.addTest(tests)
                LOGGER.info("Found unittest.TestCase: %s" % module.__name__)
    return suite

def run_unittest(suite):
    runner = unittest.TextTestRunner()
    runner.run(suite)

def main(module_names):
    suite = collect_unittest(module_names)
    if suite.countTestCases():
        run_unittest(suite)


if __name__ == '__main__':
    main(sys.argv[1:])
