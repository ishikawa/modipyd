"""

This module provides an interface to the mechanisms
used to monitor Python module file modifications.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""


import os
from errno import ENOENT
import logging
import time
from os.path import splitext

from modipyd import LOGGER
from modipyd import utils
from modipyd.module import read_module_code, \
                           collect_python_module_file
from modipyd.resolve import ModuleNameResolver
from modipyd.descriptor import ModuleDescriptor


class Monitor(object):
    """
    This class provides an interface to the mechanisms
    used to monitor Python module file modifications.
    """

    def __init__(self, filepath_or_list, search_path=None):
        from modipyd.resolve import normalize_path

        super(Monitor, self).__init__()
        self.search_path = search_path

        # paths will be used as dictionary key,
        # so make it normalized.
        paths = utils.wrap_sequence(filepath_or_list)
        self.paths = [normalize_path(i) for i in paths]
        assert not isinstance(self.paths, basestring)

        self.monitoring = False
        self.__descriptors = None
        self.__filenames = None

    @property
    def descriptors(self):
        if self.__descriptors is None:
            self.__descriptors = {}
            self.__filenames = {}
            self.refresh()
        return self.__descriptors

    #def refresh(self):
    #    from modipyd.module import collect_module_code
    #    from modipyd.descriptor import build_module_descriptors
    #    codes = list(collect_module_code(self.paths, self.search_path))
    #    self.__descriptors.clear()
    #    self.__descriptors.update(build_module_descriptors(codes))
    def refresh(self):
        assert isinstance(self.paths, (tuple, list))
        assert isinstance(self.__descriptors, dict)
        assert isinstance(self.__filenames, dict)

        # short variable names
        descriptors = self.__descriptors
        filenames = self.__filenames

        # ``monitor()`` updates all entries and
        # removes deleted entries.
        self.monitor()

        # For now, only need to check new entries.
        resolver = ModuleNameResolver(self.search_path)
        newcomers = []
        for filename, typebits in collect_python_module_file(self.paths):
            if filename in filenames:
                continue
            try:
                mc = read_module_code(filename, typebits=typebits,
                        search_path=self.search_path,
                        resolver=resolver, allow_compilation_failure=True)
            except ImportError:
                LOGGER.debug("Couldn't import file", exc_info=True)
                continue
            else:
                desc = ModuleDescriptor(mc)
                descriptors[mc.name] = desc
                filenames[filename] = desc
                newcomers.append(desc)

        for desc in newcomers:
            desc.update_dependencies(descriptors)

    def remove(self, descriptor):
        filename = splitext(descriptor.filename)[0]
        descriptors, filenames = self.__descriptors, self.__filenames

        if (descriptor.name not in descriptors or 
                filename not in filenames):
            raise KeyError(
                "No monitoring descriptor '%s'" % \
                descriptor.name)

        descriptor.clear_dependencies()
        del descriptors[descriptor.name]
        del filenames[filename]


    def monitor(self):
        descriptors = self.descriptors
        modifieds = []
        removals = []

        for desc in descriptors.itervalues():
            try:
                if desc.modified():
                    desc.reload(descriptors)
                    modifieds.append(desc)
            except os.error, e:
                if e.errno == ENOENT:
                    # No such file
                    LOGGER.info("Removed:\n%s" % desc)
                    removals.append(desc)
                else:
                    raise

        # Remove removal entries
        for desc in removals:
            try:
                self.remove(desc)
            except KeyError:
                LOGGER.debug(
                    "No monitoring descriptor '%s' for removal" % desc.name,
                    exc_info=True)

        del removals
        return modifieds

    def start(self):
        descriptors = self.descriptors

        # Logging
        if LOGGER.isEnabledFor(logging.INFO):
            desc = "\n".join([
                desc.describe(indent=4)
                for desc in descriptors.itervalues()])
            LOGGER.info("Monitoring:\n%s" % desc)

        # Prior to Python 2.5, the ``yiled`` statement is not
        # allowed in the ``try`` clause of a ``try ... finally``
        # construct.
        try:
            self.monitoring = True
            while descriptors and self.monitoring:
                time.sleep(1)
                for modified in self.monitor():
                    yield modified
            else:
                LOGGER.info("Terminating monitor %s" % str(self))
        except:
            self.monitoring = False
            raise

    def stop(self):
        self.monitoring = False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
