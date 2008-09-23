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

    # Construct ``ModuleMonitor``s
    modules = {}
    for module in module_list:
        modules[module.name] = ModuleMonitor(module)

    # Analyze module dependencies
    for module in modules.itervalues():
        dependent_names = []
        for name, fromlist in module.module.imports:
            if not fromlist:
                dependent_names.append(name)
            for sym in fromlist:
                quolified_name = '.'.join([name, sym])
                if quolified_name in modules:
                    dependent_names.append(quolified_name)
                else:
                    # The fromlist includes contents of
                    # module named `name`.
                    dependent_names.append(name)

        for name in dependent_names:
            if name in modules:
                module.add_dependency(modules[name])

    # Logging
    if LOGGER.isEnabledFor(logging.INFO):
        desc = "\n".join([m.describe() for m in modules.itervalues()])
        LOGGER.info("Monitoring:\n%s" % desc)

    while modules:
        time.sleep(1)
        for module in modules.itervalues():
            if module.update():
                yield module


# ----------------------------------------------------------------
# ModuleMonitor
# ----------------------------------------------------------------
def _format_monitor_list(modules):
    import pprint
    return pprint.pformat(
        list(m.name for m in modules))

class ModuleMonitor(object):

    def __init__(self, module):
        super(ModuleMonitor, self).__init__()
        self.module = module
        self.mtime = None
        self.update_mtime()

        self.dependencies = set()
        self.reverse_dependencies = set()

    def describe(self):
        messages = []
        messages.append('%s: %s' % (self.name, self))
        messages.append('  Dependencies: %s' % _format_monitor_list(
            self.dependencies))
        messages.append('  Reverse: %s' % _format_monitor_list(
            self.reverse_dependencies))
        return "\n".join(messages)

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
            return self.mtime is None or mtime > self.mtime
        finally:
            self.mtime = mtime

    def add_dependency(self, module):
        self.dependencies.add(module)
        module.add_reverse_dependency(self)

    def add_reverse_dependency(self, module):
        self.reverse_dependencies.add(module)

    def __str__(self):
        return str(self.module)


