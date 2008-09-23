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
from modipyd.module import collect_module_code


def monitor(filepath_or_list):
    paths = utils.wrap_sequence(filepath_or_list)
    assert not isinstance(paths, basestring)
    module_codes = list(collect_module_code(paths))
    for modified in monitor_module_codes(module_codes):
        yield modified

def build_module_descriptors(module_codes):

    def analyze_dependent_names(descriptor):
        for name, fromlist in descriptor.module_code.imports:
            # 'import MODULE'
            if not fromlist:
                yield name
            # 'from MODULE import SYMBOLS'
            for sym in fromlist:
                quolified_name = '.'.join([name, sym])
                if quolified_name in descriptors:
                    # The quolified name referes a submodule
                    yield quolified_name
                else:
                    # The quolified name referes a property
                    # of the module, so it depends imporintg module.
                    yield name

    # Construct ``ModuleDescriptor`` mappings
    descriptors = dict([
        (code.name, ModuleDescriptor(code))
        for code in module_codes])

    # Dependency Analysis
    for descriptor in descriptors.itervalues():
        for name in analyze_dependent_names(descriptor):
            if name in descriptors:
                descriptor.add_dependency(descriptors[name])
    return descriptors

def monitor_module_codes(module_codes):
    """Monitoring ``modipyd.module.Module``s"""
    descriptors = build_module_descriptors(module_codes)

    # Logging
    if LOGGER.isEnabledFor(logging.INFO):
        desc = "\n".join([
            desc.describe(indent=4)
            for desc in descriptors.itervalues()])
        LOGGER.info("Monitoring:\n%s" % desc)

    while descriptors:
        time.sleep(1)
        for desc in descriptors.itervalues():
            if desc.update():
                yield desc


# ----------------------------------------------------------------
# ModuleDescriptor
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


class ModuleDescriptor(object):

    def __init__(self, module_code):
        super(ModuleDescriptor, self).__init__()
        self.__module_code = module_code
        self.__mtime = None
        self.update_mtime()

        self.__dependencies = OrderedSet()
        self.__reverse_dependencies = OrderedSet()

    def __str__(self):
        return str(self.module_code)

    def __eq__(self, other):
        return (self is other or
                    (isinstance(other, type(self)) and
                     self.module_code == other.module_code))

    def __hash__(self):
        return hash(self.module_code)

    def describe(self, indent=1, width=80, depth=None):
        """
        Return the formatted representation of ``ModuleDescriptor``
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
    def dependencies(self):
        return tuple(self.__dependencies)

    @property
    def reverse_dependencies(self):
        return tuple(self.__reverse_dependencies)

    @property
    def module_code(self):
        return self.__module_code

    @property
    def name(self):
        return self.module_code.name

    @property
    def filepath(self):
        return self.module_code.filepath

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

    def add_dependency(self, descriptor):
        self.__dependencies.append(descriptor)
        descriptor.add_reverse_dependency(self)

    def add_reverse_dependency(self, descriptor):
        self.__reverse_dependencies.append(descriptor)

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
