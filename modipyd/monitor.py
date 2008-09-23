"""

This module provides an interface to the mechanisms
used to monitor Python module file modifications.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import os
import logging
import time
from modipyd import LOGGER
from modipyd import utils
from modipyd.module import collect_python_module


def monitor(filepath_or_list):
    paths = utils.wrap_sequence(filepath_or_list)
    assert not isinstance(paths, basestring)
    modules = list(collect_python_module(paths))
    for modified in monitor_modules(modules):
        yield modified

def monitor_modules(module_list):
    """Monitoring ``modipyd.module.Module``s"""

    def analyze_dependent_names(module):
        for name, fromlist in module.module.imports:
            # 'import MODULE'
            if not fromlist:
                yield name
            # 'from MODULE import SYMBOLS'
            for sym in fromlist:
                quolified_name = '.'.join([name, sym])
                if quolified_name in modules:
                    # The quolified name referes a submodule
                    yield quolified_name
                else:
                    # The quolified name referes a property
                    # of the module, so it depends imporintg module.
                    yield name

    # Construct ``ModuleMonitor`` mappings
    modules = dict([
        (module.name, ModuleMonitor(module))
        for module in module_list])

    # Dependency Analysis
    for module in modules.itervalues():
        for name in analyze_dependent_names(module):
            if name in modules:
                module.add_dependency(modules[name])

    # Logging
    if LOGGER.isEnabledFor(logging.INFO):
        desc = "\n".join([m.describe(indent=4) for m in modules.itervalues()])
        LOGGER.info("Monitoring:\n%s" % desc)

    while modules:
        time.sleep(1)
        for module in modules.itervalues():
            if module.update():
                yield module


# ----------------------------------------------------------------
# ModuleMonitor
# ----------------------------------------------------------------
class OrderedSet(object):

    def __init__(self, items=None):
        super(OrderedSet, self).__init__()
        self.__items = []
        self.__set = set()
        self.update(items or ())

    def __len__(self):
        return len(self.__items)

    def __iter__(self):
        return iter(self.__items)

    def __contains__(self, item):
        return item in self.__set

    def __str__(self):
        return str(self.__items)

    def __repr__(self):
        return repr(self.__items)

    def update(self, items):
        for i in items:
            self.add(i)

    def add(self, item):
        if item not in self.__set:
            self.__items.append(item)
            self.__set.add(item)

    append = add

    def remove(self, item):
        self.__items.remove(item)
        self.__set.remove(item)

    def clear(self):
        self.__items[:] = []
        self.__set.clear()


class ModuleMonitor(object):

    def __init__(self, module):
        super(ModuleMonitor, self).__init__()
        self.__module = module
        self.__mtime = None
        self.update_mtime()

        self.__dependencies = OrderedSet()
        self.__reverse_dependencies = OrderedSet()

    def __str__(self):
        return str(self.module)

    def __eq__(self, other):
        return (self is other or
                    (isinstance(other, type(self)) and
                     self.module == other.module))

    def __hash__(self):
        return hash(self.module)

    def describe(self, indent=1, width=80, depth=None):
        """
        Return the formatted representation of ``ModuleMonitor``
        as a string. *indent*, *width* and *depth* will be passed to
        the ``PrettyPrinter`` constructor as formatting parameters.
        """
        def _format_monitor_list(modules):
            import re
            from pprint import pformat

            s = pformat(list(m.name for m in modules),
                indent=indent, width=width, depth=depth)
            # bug?
            return re.sub(r'\[( +)', "[\n\\1 ", s)

        messages = []
        messages.append('%s: %s' % (self.name, self.filepath))
        messages.append('  Dependencies: %s' % _format_monitor_list(
            self.__dependencies))
        messages.append('  Reverse: %s' % _format_monitor_list(
            self.__reverse_dependencies))
        return "\n".join(messages)

    @property
    def module(self):
        return self.__module

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
            return self.__mtime is None or mtime > self.__mtime
        finally:
            self.__mtime = mtime

    def add_dependency(self, module):
        self.__dependencies.append(module)
        module.add_reverse_dependency(self)

    def add_reverse_dependency(self, module):
        self.__reverse_dependencies.append(module)

    def walk(self):
        """Walking reverse dependency (includes self)"""
        cycle = False
        yield self
        for m in self.__reverse_dependencies:
            for mm in m.walk():
                if mm is self:
                    # cycle detected
                    if cycle:
                        LOGGER.info("Cycle break: %s" % self.name)
                        break
                    else:
                        LOGGER.info("Cycle detected: %s" % self.name)
                        cycle = True
                        break
                yield mm
