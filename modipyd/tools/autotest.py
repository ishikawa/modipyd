"""
autotest
================================================

quoted from http://www.zenspider.com/ZSS/Products/ZenTest/

> Improves feedback by running tests continuously.
> Continually runs tests based on files you've changed.
> Get feedback as soon as you save. Keeps you in your editor
> allowing you to get stuff done faster.
> Focuses on running previous failures until you've fixed them.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""
import os
import sys
import logging
from optparse import OptionParser

from modipyd import LOGGER, utils
from modipyd.monitor import Monitor


# ----------------------------------------------------------------
# Version
# ----------------------------------------------------------------
MAJOR_VERSION = 0
MINOR_VERSION = 1
VERSION_STRING = "%d.%d" % (MAJOR_VERSION, MINOR_VERSION)


# ----------------------------------------------------------------
# Notification Observer
# ----------------------------------------------------------------
def testcase_module(module_descriptor):
    # We can't use ``unittest.TestLoader`` to loading tests,
    # bacause ``TestLoader`` imports (execute) module code.
    # If imported/executed module have a statement such as
    # ``sys.exit()``, ...program exit!

    modcode = module_descriptor.module_code
    assert modcode

    # How to check unittest.TestCase
    # ============================================
    # 1. For all class definition in module code
    # 2. Check class is derived from base class(s)
    # 3. Check base class(s) is imported from another module
    # 4. Load base class(s) from that module
    #    Notes: Assume the module contains base class does not have
    #           a dangerous code such as ``sys.exit``.
    # 5. Check loaded class is unittest.TestCase or its subclass

    # Construct imported symbols.
    # This is used in phase 3.
    #
    #   symbols ::= { symbol: parent module or '', ... }
    #
    symbols = dict([
        (imp[0], utils.split_module_name(imp[1])[0])
        for imp in modcode.imports])

    # 1. For all class definition in module code
    for klass in modcode.classdefs:

        # 2. Check class is derived from base class(s)
        bases = klass[1]
        if not bases:
            continue

        # 3. Check base class(s) is imported from another module
        for base in bases:
            # Search imported symbol that is class name or module name
            symbol = base
            names = base.split('.')
            if len(names) > 1:
                symbol = '.'.join(names[:-1])

            # Not an imported base class
            if not symbol in symbols:
                continue

            if symbols[symbol]:
                names = symbols[symbol].split('.') + names

            assert len(names) > 1, "names must be qualified class name"
            LOGGER.debug("'%s' is derived from "
                "imported class '%s'" % (base, '.'.join(names)))

            name = '.'.join(names)
            try:
                baseclass = utils.import_component(name)
            except (ImportError, AttributeError):
                LOGGER.warn("Exception occurred "
                    "while importing component '%s'" % name,
                    exc_info=True)
            else:
                # 5. Check loaded class is unittest.TestCase or its subclass
                import types
                import unittest

                return (isinstance(baseclass, (type, types.ClassType)) and
                        issubclass(baseclass, unittest.TestCase))

    return False


def observe(module_descriptor):

    # Walking dependency graph in imported module to
    # module imports order.
    for descriptor in module_descriptor.walk():
        LOGGER.info("-> Affected: %s" % descriptor.name)
        if testcase_module(descriptor):
            LOGGER.info("=> Loading:  %s" % descriptor.name)


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def main(options, filepath):
    """
    Monitoring modules on the search path ``path``. If ``path`` is
    a list of directory names, each directory is searched for files
    with '.py' suffix. They are also inserted into ``sys.path`` so that
    program can import monitoring modules.
    """
    # options handling
    if options.verbose:
        LOGGER.setLevel(logging.INFO)
    if options.debug:
        LOGGER.setLevel(logging.DEBUG)

    # So many projects contain its modules and packages
    # at top level directory, modipyd inserts current directory
    # in ``sys.path`` module search path variable for convenience.
    sys.path.insert(0, os.getcwd())

    # start monitoring
    try:

        monitor = Monitor(filepath)
        for modified in monitor.start():
            LOGGER.info("Modified:\n%s" % modified.describe(indent=4))
            observe(modified)

    except KeyboardInterrupt:
        LOGGER.debug('KeyboardInterrupt', exc_info=True)

def run():
    """Standalone program interface"""
    parser = OptionParser(
        usage="usage: %prog [options] [files or directories]",
        version=("%prog " + VERSION_STRING))

    parser.add_option("-v", "--verbose",
        action="store_true", dest="verbose", default=False,
        help="Make the operation more talkative")
    parser.add_option("--debug",
        action="store_true", dest="debug", default=False,
        help="Make the operation more talkative (debug mode)")

    (options, args) = parser.parse_args()
    main(options, args or '.')


if __name__ == '__main__':
    run()
