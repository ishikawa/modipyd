"""

This module provides useful functions and class ``ModuleDescriptor``
for managing annotations of module.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import os
from modipyd import LOGGER, utils
from modipyd.utils import OrderedSet
from modipyd.resolve import resolve_relative_modulename


def build_module_descriptors(module_codes):

    def import_name_candidates(import_names):
        candidates = []
        for name in import_names:
            if name not in descriptors:
                # The qualified name referes a property
                # of the module, so it depends imporintg module.
                candidates.append(utils.split_module_name(name)[0])
            else:
                candidates.append(name)
        return candidates

    def analyze_dependent_names(descriptor):
        for imp in descriptor.module_code.imports:
            # name is the fully qualified name
            name, level = imp[1], imp[2]
            assert name and level is not None

            if level == 0:
                # 0 means only perform absolute imports
                for item in import_name_candidates([name]):
                    yield item
            elif level == -1:
                # -1 which indicates both absolute and relative imports
                # will be attempted
                names = []
                if descriptor.package_name:
                    names.append('.'.join((descriptor.package_name, name)))
                names.append(name)

                for item in import_name_candidates(names):
                    yield item

            else:
                # Relative imports
                assert descriptor.package_name
                resolved_name = resolve_relative_modulename(
                    name, descriptor.package_name, level)
                for item in import_name_candidates([resolved_name]):
                    yield item

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


class ModuleDescriptor(object):

    def __init__(self, module_code):
        super(ModuleDescriptor, self).__init__()
        self.__module_code = module_code
        self.__mtime = None
        self.update_mtime()

        self.__dependencies = OrderedSet()
        self.__reverse_dependencies = OrderedSet()

    def __str__(self):
        return "<ModuleDescriptor '%s' (%s)>" % (self.name, self.filename)

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
    def package_name(self):
        return self.module_code.package_name

    @property
    def filename(self):
        return self.module_code.filename

    def update(self):
        if self.update_mtime():
            LOGGER.info(
                "Reload module descriptor '%s' at %s" % \
                (self.name, self.filename))

            try:
                self.module_code.reload()
            except SyntaxError:
                # SyntaxError is OK
                LOGGER.warn("SyntaxError found in %s" % self.filename,
                    exc_info=True)
            else:
                self.update_dependencies()
                return True
        return False

    def update_dependencies(self):
        LOGGER.debug("Update dependencies %s" % str(self))
        LOGGER.info("Dependencies updated:\n%s" % self.describe())

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

    def walk_dependency_graph(self, reverse=False):
        """
        Walking on the module dependency graph.
        *reverse* is a boolean value. If set to ``True``,
        then the walking is in an imported module (self included)
        to a module imports order.
        """
        if reverse:
            graph_name = 'reverse_dependencies'
        else:
            graph_name = 'dependencies'

        # self first
        yield self

        # Use Breadth First Search (BFS) algorithm
        vqueue = [self]
        discovered = set(vqueue)
        while vqueue:
            u = vqueue.pop()
            for v in getattr(u, graph_name):
                if v not in discovered:
                    discovered.add(v)
                    vqueue.append(v)
                    yield v


if __name__ == "__main__":
    import doctest
    doctest.testmod()
