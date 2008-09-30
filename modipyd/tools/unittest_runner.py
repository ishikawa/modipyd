"""
A command-line program that runs a set of tests; this is primarily for making
test modules conveniently executable.

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""

import unittest
from optparse import OptionParser

from modipyd import LOGGER, utils
from modipyd.utils import import_component


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

def main(module_names, test_runner_class='unittest.TextTestRunner'):
    suite = collect_unittest(module_names)
    if not suite.countTestCases():
        return
    
    testRunner = import_component(test_runner_class)
    runner = testRunner()
    runner.run(suite)


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] modules")
    parser.add_option("-r", "--runner", default='unittest.TextTestRunner',
        action="store", dest="runner", metavar='CLASS_NAME',
        help="qualified name of the unittest.TestRunner subclass "
             "(default: unittest.TextTestRunner)")

    options, args = parser.parse_args()
    main(args, options.runner)
