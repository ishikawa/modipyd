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

from modipyd import LOGGER
from modipyd import utils


class Monitor(object):
    """
    This class provides an interface to the mechanisms
    used to monitor Python module file modifications.
    """

    def __init__(self, filepath_or_list, search_path=None):
        super(Monitor, self).__init__()
        self.paths = utils.wrap_sequence(filepath_or_list)
        assert not isinstance(self.paths, basestring)
        self.search_path = search_path
        self.monitoring = False
        self.__descriptors = None

    @property
    def descriptors(self):
        if self.__descriptors is None:
            self.__descriptors = {}
            self.refresh()
        return self.__descriptors

    def refresh(self):
        from modipyd.module import collect_module_code
        from modipyd.descriptor import build_module_descriptors

        codes = list(collect_module_code(self.paths, self.search_path))
        self.__descriptors.clear()
        self.__descriptors.update(build_module_descriptors(codes))

    def monitor(self):
        descriptors = self.descriptors
        modifieds = []
        removals = []

        for name, desc in descriptors.iteritems():
            try:
                if desc.modified():
                    desc.reload(descriptors)
                    modifieds.append(desc)
            except os.error, e:
                if e.errno == ENOENT:
                    # No such file
                    LOGGER.info("Removed:\n%s" % desc)
                    removals.append(name)
                else:
                    raise

        # Remove removal entries
        for name in removals:
            if name not in descriptors:
                continue
            desc = descriptors[name]
            desc.clear_dependencies()
            del descriptors[name]

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
