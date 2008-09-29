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
from modipyd.utils.decorators import require


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
        self.__failures = None

    @property
    def descriptors(self):
        if self.__descriptors is None:
            self.__descriptors = {}
            self.__filenames = {}
            self.__failures = set()
            entries = list(self.refresh())
            LOGGER.debug("%d descriptoes" % len(entries))
        return self.__descriptors

    @require(descriptor=ModuleDescriptor)
    def remove(self, descriptor):
        filename = splitext(descriptor.filename)[0]
        descriptors, filenames = self.__descriptors, self.__filenames

        if (descriptor.name not in descriptors or 
                filename not in filenames):
            raise KeyError(
                "No monitoring descriptor '%s'" % \
                descriptor.name)

        LOGGER.debug("Removed: %s" % descriptor.describe())
        descriptor.clear_dependencies()
        del descriptors[descriptor.name]
        del filenames[filename]

    def refresh(self):
        assert isinstance(self.paths, (tuple, list))
        assert isinstance(self.__descriptors, dict)
        assert isinstance(self.__filenames, dict)
        assert isinstance(self.__failures, set)

        # localize variable access to minimize overhead
        # and to reduce the visual noise.
        descriptors = self.__descriptors
        filenames = self.__filenames
        failures = self.__failures

        # ``monitor()`` updates all entries and
        # removes deleted entries.
        for modified in self.monitor():
            yield modified

        # For now, only need to check new entries.
        resolver = ModuleNameResolver(self.search_path)
        newcomers = []
        for filename, typebits in collect_python_module_file(self.paths):
            if filename in filenames or filename in failures:
                continue
            try:
                mc = read_module_code(filename, typebits=typebits,
                        search_path=self.search_path,
                        resolver=resolver, allow_compilation_failure=True)
            except ImportError:
                LOGGER.debug("Couldn't import file", exc_info=True)
                failures.add(filename)
                continue
            else:
                desc = ModuleDescriptor(mc)
                descriptors[mc.name] = desc
                filenames[filename] = desc
                # modifieds += new entries
                newcomers.append(desc)
                LOGGER.debug("Added: %s" % desc.describe())

        # Since there are some entries already refer new entry,
        # we need to update dependencies of all entries
        for desc in descriptors.itervalues():
            desc.update_dependencies(descriptors)

        # Notify caller what entries are appended
        for newcomer in newcomers:
            yield newcomer


    def monitor(self):
        descriptors = self.descriptors
        removals = []

        for desc in descriptors.itervalues():
            try:
                if desc.modified():
                    desc.reload(descriptors)
                    yield desc
            except os.error, e:
                if e.errno == ENOENT:
                    # No such file
                    removals.append(desc)
                else:
                    raise

        # Remove removal entries
        for desc in removals:
            try:
                # yield before remove
                yield desc
                self.remove(desc)
            except KeyError:
                LOGGER.debug(
                    "No monitoring descriptor '%s' for removal" % desc.name,
                    exc_info=True)

    @require(interval=(int, float), refresh_factor=int)
    def start(self, interval=1.0, refresh_factor=5):
        if refresh_factor < 1:
            raise RuntimeError("refresh_factor must be greater or eqaul to 1")
        if interval <= 0:
            raise RuntimeError("refresh_factor must not be negative or 0")

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

            times = 0
            while descriptors and self.monitoring:

                time.sleep(interval)
                times += 1

                if times % 5 == 0:
                    monitor = self.refresh()
                else:
                    monitor = self.monitor()

                for modified in monitor:
                    if not self.monitoring:
                        break
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
