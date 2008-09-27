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


def _update_module_dependencies(module_descriptor, descriptors):

    def _modulename(name):
        if name not in descriptors and '.' in name:
            # The qualified name maybe refere a property
            # of the module, so it depends that module.
            module_name = utils.split_module_name(name)[0]
            assert module_name
            return module_name
        else:
            return name

    def _dependent_names(descriptor):
        #print "analyze_dependent_names: %s" % descriptor.name
        for imp in descriptor.module_code.imports:
            #print "  import: %s" % str(imp)
            # name is the fully qualified name
            name, level = imp[1], imp[2]
            assert name and level is not None

            modulename = name
            if level == 0:
                # 0 means only perform absolute imports
                modulename = _modulename(name)
            elif level == -1:
                # -1 which indicates both absolute and relative imports
                # will be attempted

                # Implicit relative import
                if descriptor.package_name:
                    modulename = '.'.join((descriptor.package_name, name))
                    if modulename not in descriptors and '.' in name:
                        modulename = _modulename(modulename)

                # Implicit relative import failed
                if modulename not in descriptors:
                    modulename = _modulename(name)

            else:
                # Relative imports
                assert descriptor.package_name
                modulename = resolve_relative_modulename(
                    name, descriptor.package_name, level)
                modulename = _modulename(modulename)

            if modulename in descriptors:
                yield modulename

    # Dependency Analysis
    module_descriptor.clear_dependencies()
    for dependent_name in _dependent_names(module_descriptor):
        #print "  -> dependent: ", name
        module_descriptor.add_dependency(
                descriptors[dependent_name])


def build_module_dependencies(descriptors):
    # Dependency Analysis
    for descriptor in descriptors.itervalues():
        descriptor.update_dependencies(descriptors)


def build_module_descriptors(module_codes):
    # Construct ``ModuleDescriptor`` mappings
    descriptors = dict([
        (code.name, ModuleDescriptor(code))
        for code in module_codes])
    build_module_dependencies(descriptors)
    return descriptors


class ModuleDescriptor(object):

    def __init__(self, module_code):
        super(ModuleDescriptor, self).__init__()
        self.__module_code = module_code
        self.__mtime = None
        self.modified()

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

    def reload(self, descriptors, co=None):
        """
        Reload module code, update dependency graph
        """
        LOGGER.info(
            "Reload module descriptor '%s' at %s" % \
            (self.name, self.filename))

        try:
            self.module_code.reload(co)
        except SyntaxError:
            # SyntaxError is OK
            LOGGER.warn("SyntaxError found in %s" % self.filename,
                exc_info=True)
        else:
            self.update_dependencies(descriptors)

    def modified(self):
        """Update modification time and return ``True`` if modified"""
        mtime = self.__mtime
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

    def remove_reverse_dependencies(self, descriptor):
        self.__reverse_dependencies.remove(descriptor)

    def update_dependencies(self, descriptors):
        LOGGER.debug("Update dependencies of '%s'" % self.name)
        _update_module_dependencies(self, descriptors)

    def clear_dependencies(self):
        for d in self.__dependencies:
            d.remove_reverse_dependencies(self)
        self.__dependencies.clear()

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
