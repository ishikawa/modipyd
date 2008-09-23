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
    paths = utils.wrap_sequence(filepath_or_list)
    assert not isinstance(paths, basestring)
    module_codes = list(collect_module_code(paths))
    for modified in monitor_module_codes(module_codes):
        yield modified

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
