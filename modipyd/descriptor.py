"""

This module provides useful functions and class ``ModuleDescriptor``
for managing annotations of module.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import os
from modipyd import LOGGER
from modipyd import utils


def build_module_descriptors(module_codes):

    def analyze_dependent_names(descriptor):
        for imp in descriptor.module_code.imports:
            name = imp[1]
            if name not in descriptors:
                # The qualified name referes a property
                # of the module, so it depends imporintg module.
                yield utils.split_module_name(name)[0]
            else:
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


class OrderedSet(object):

    def __init__(self, items=None):
        super(OrderedSet, self).__init__()
        self.__items = []
        self.__set = set()
        self.update(items or ())

    def __len__(self):
        return len(self.__items)

    def __getitem__(self, i):
        return self.__items[i]

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
        messages.append('%s: %s' % (self.name, self.filename))
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
    def filename(self):
        return self.module_code.filename

    def update(self):
        return self.update_mtime()

    def update_mtime(self):
        """Update modification time and return ``True`` if modified"""
        mtime = None
        try:
            mtime = os.path.getmtime(self.filename)
            return self.__mtime is None or mtime > self.__mtime
        finally:
            self.__mtime = mtime

    def add_dependency(self, descriptor):
        self.__dependencies.append(descriptor)
        descriptor.add_reverse_dependency(self)

    def add_reverse_dependency(self, descriptor):
        self.__reverse_dependencies.append(descriptor)

    def walk(self):
        """
        Walking dependency graph in imported module to
        module imports order (includes itself).
        """
        yield self
        # Use Breadth First Search (BFS) algorithm
        L = [self]
        discovered = set(L)
        while L:
            u = L.pop()
            for v in u.reverse_dependencies:
                if v not in discovered:
                    discovered.add(v)
                    L.append(v)
                    yield v

    def import_module(self):
        try:
            return utils.import_module(self.name)
        except ImportError:
            LOGGER.warn("ImportError occurred while "
                "importing module '%s'" % (self.name))
            if (self.filename.endswith('.pyc') or
                    self.filename.endswith('.pyo')):
                LOGGER.warn("Suggestion: An orphan file? %s" % self.filename)
            raise
