"""

This module provides an interface to the mechanisms
used to monitor Python module file modifications.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import logging
import time
from modipyd import LOGGER
from modipyd import utils
from modipyd.module import collect_module_code
from modipyd.descriptor import build_module_descriptors


def monitor(filepath_or_list):
    return Monitor(filepath_or_list).start()


class Monitor(object):
    """
    This class provides an interface to the mechanisms
    used to monitor Python module file modifications.
    """

    def __init__(self, filepath_or_list):
        super(Monitor, self).__init__()
        self.paths = utils.wrap_sequence(filepath_or_list)
        assert not isinstance(self.paths, basestring)
        self.__descriptors = {}

    def start(self):
        module_codes = list(collect_module_code(self.paths))
        descriptors = build_module_descriptors(module_codes)
        self.__descriptors = descriptors

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

    def stop(self):
        pass

    @property
    def descriptors(self):
        return self.__descriptors
