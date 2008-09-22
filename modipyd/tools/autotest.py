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
import time
import logging
import unittest
from optparse import OptionParser

from modipyd import utils, LOGGER
from modipyd.pyscript import PyScript
from modipyd.module import Module, collect_python_module


# ----------------------------------------------------------------
# Version
# ----------------------------------------------------------------
MAJOR_VERSION = 0
MINOR_VERSION = 1
VERSION_STRING = "%d.%d" % (MAJOR_VERSION, MINOR_VERSION)


# ----------------------------------------------------------------
# API, Functions, Classes...
# ----------------------------------------------------------------
def collect_pyscript(filepath):
    scripts = []
    for filename in utils.collect_files(filepath):
        if filename.endswith('.py'):
            try:
                modfile = PyScript(filename)
                LOGGER.info("Module Loaded: %s" % modfile.module)
            except os.error:
                LOGGER.warn(
                    "The file at %s does not exist"
                    " or is inaccessible, ignore." % filename)
            except ImportError:
                LOGGER.info("Couldn't import file at %s, ignore" % filename)
            else:
                scripts.append(modfile)

    # uniqfy
    return list(set(scripts))


def monitor(modules):
    """WARNING: This method can modify ``scripts`` list."""
    assert isinstance(modules, list)
    for m in modules:
        print m

    while modules:
        time.sleep(1)
        # For in-place deletion (avoids copying the list),
        # Don't delete anything earlier in the list than
        # the current element through.
        for i, m in enumerate(reversed(modules)):
            if not os.path.exists(m.filepath):
                del modules[-(i+1)]


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def collect_unittest(scripts):
    """
    Search ``unittest.TestCase`` classes in scripts,
    return ``unittest.TestSuite`` instance.
    """
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for script in scripts:
        tests = loader.loadTestsFromModule(script.module)
        if tests.countTestCases():
            suite.addTest(tests)
            LOGGER.info("Running test: %s" % script.module.__name__)
    return suite

def run_unittest(scripts):
    suite = collect_unittest(scripts)
    if suite.countTestCases():
        runner = unittest.TextTestRunner()
        runner.run(suite)

def on_module_modified(modified, scripts):
    import modulefinder
    from modipyd.utils import find_modulename

    mappings = {}
    dependancies = {}

    # Mapping module name -> script
    for script in scripts:
        try:
            modname = find_modulename(script.filename)
        except ImportError:
            LOGGER.warn(
                "Couldn't import file at %s, ignore" % script.filename,
                exc_info=True)
        else:
            mappings[modname] = script

    # Construct dependancy graph
    for name, script in mappings.iteritems():
        finder = modulefinder.ModuleFinder()
        finder.run_script(script.filename)
        for module_name, module in finder.modules.iteritems():
            if module_name == name or not module.__file__:
                continue
            if module_name in mappings:
                dependancies.setdefault(module_name, set()).add(name)

    def iterate_dependancies(module_name):
        if module_name in dependancies:
            for n in dependancies[module_name]:
                yield n
                for m in iterate_dependancies(n):
                    yield m

    # Inspect modified script dependancies
    try:
        modname = find_modulename(modified.filename)
        dependent_names = set(iterate_dependancies(modname))
    except ImportError:
        LOGGER.warn(
            "Couldn't import file at %s, ignore" % script.filename,
            exc_info=True)
    else:
        # dependent modules + modified module itself
        #
        # This dependent order is **important**, because a dependent
        # module might refer target module's symbols (variable, class, ... etc).
        #
        dependent_scripts = [mappings[it] for it in dependent_names]
        dependent_scripts.insert(0, modified)
        for script in dependent_scripts:
            LOGGER.info("Reload Module: %s" % script.module)
            script.load_module(True)
        run_unittest(dependent_scripts)


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
        # Make filepath list.
        filepath = utils.wrap_sequence(filepath)
        assert not isinstance(filepath, basestring)
        modules = list(collect_python_module(filepath))

        for modified in monitor(modules):
            LOGGER.info("Modified %s" % modified)
            on_module_modified(modified, scripts)

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
    main(options, args or os.getcwd())


if __name__ == '__main__':
    run()
