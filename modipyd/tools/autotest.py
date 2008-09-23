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
import pprint
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
class ModuleMonitor(object):

    def __init__(self, module):
        super(ModuleMonitor, self).__init__()
        self.module = module
        self.mtime = None
        self.update_mtime()

        self.dependencies = set()
        self.reverse_dependencies = set()

    @property
    def name(self):
        return self.module.name

    @property
    def filepath(self):
        return self.module.filepath

    def update(self):
        return self.update_mtime()

    def update_mtime(self):
        """Update modification time and return ``True`` if modified"""
        mtime = None
        try:
            mtime = os.path.getmtime(self.filepath)
            return self.mtime is None or mtime > self.mtime
        finally:
            self.mtime = mtime

    def add_dependency(self, module):
        self.dependencies.add(module)
        module.add_reverse_dependency(self)

    def add_reverse_dependency(self, module):
        self.reverse_dependencies.add(module)

    def __str__(self):
        return str(self.module)


def monitor(module_list):

    def _format_module_list(modules):
        return pprint.pformat(
            list(m.name for m in modules))

    def _format_module_dict(modules):
        messages = []
        for name, m in modules.iteritems():
             messages.append('%s: %s' % (name, m))
             messages.append('  Dependencies: %s' % _format_module_list(
                m.dependencies))
             messages.append('  Reverse: %s' % _format_module_list(
                m.reverse_dependencies))
        return "\n".join(messages)

    # Construct ``ModuleMonitor``s
    modules = {}
    for m in module_list:
        modules[m.name] = ModuleMonitor(m)

    # Analyze module dependencies
    for modname, module in modules.iteritems():
        dependent_names = []
        for name, fromlist in module.module.imports:
            dependent_names.append(name)
            for sym in fromlist:
                quolified_name = '.'.join([name, sym])
                dependent_names.append(quolified_name)

        for name in dependent_names:
            if name in modules:
                module.add_dependency(modules[name])

    # Logging
    if LOGGER.isEnabledFor(logging.INFO):
        LOGGER.info("Monitoring:\n%s" % _format_module_dict(modules))

    while modules:
        time.sleep(1)
        for modname, module in modules.iteritems():
            if module.update():
                yield module


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def run_unittest(suite):
    if suite.countTestCases():
        runner = unittest.TextTestRunner()
        runner.run(suite)

def walk_dependencies(module, dependencies):
    yield module
    for mod1 in dependencies:
        for mod2 in walk_dependencies(mod1, mod1.reverse_dependencies):
            yield mod2

def collect_affected_unittests(module):
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader

    walked = set()
    for mod in walk_dependencies(module, module.reverse_dependencies):
        if mod.name in walked:
            continue
        else:
            walked.add(mod.name)

        # TODO: Don't depends on filename pattern
        LOGGER.info("  Affected: %s" % mod)
        if os.path.basename(mod.filepath).startswith('test_'):
            m = utils.import_module(mod.name)
            tests = loader.loadTestsFromModule(m)
            if tests.countTestCases():
                suite.addTest(tests)
                LOGGER.info("Running test: %s" % m.__name__)
    return suite


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
            from pprint import pformat
            LOGGER.info("Modified %s" % modified)
            LOGGER.info("  Dependencies: %s" % 
                pformat(list(str(x) for x in modified.dependencies)))
            LOGGER.info("  Reverse Dependencies: %s" % 
                pformat(list(str(x) for x in modified.reverse_dependencies)))

            suite = collect_affected_unittests(modified)
            run_unittest(suite)

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
