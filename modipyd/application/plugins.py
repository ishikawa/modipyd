"""
Modipyd Plugin Interface
================================================

This document specifies a Modipyd plugin architecture and standard interface
between Modipyd runtime and plugin.


Specification Overview
------------------------------------------------

The **plugin object** is simply a callable object that accepts three arguments.
The term "object" should not be mis constructed as requiring an acutual
object instance: a function, method, class, or instance with a ``__call__``
method are all acceptable for use as a plugin object. **Note:** Plugin objects
must be able to invoked more than once.

Here are two example plugin objects; one is a function, and the other
is a class:

    def simple_plugin(event, monitor, context):
        \"\"\"Simplest possible plugin object\"\"\"
        print "Event occurred:", event.type
        print "Modified module:", event.descriptor
    
    class SimplePlugin(object):
        \"\"\"Produce the same output, but using a class\"\"\"
    
        def __init__(self, event, monitor, context):
            self.event = event
    
        def __call__(self):
            print "Event occurred:", self.event.type
            print "Modified module:", self.event.descriptor

If the plugin object returns callable object (it is optional), it is
called with no arguments immediately.

With above example, The ``PluginClass`` is the "plugin object" here,
so calling it returns an instance of ``PluginClass``, which is
the "object callable".


Specification Details
------------------------------------------------

The plugin object must accept three **positional** arguments.
For the sake ofillustration, we have named them ``event``,
``monitor`` and ``context``,but they are not required to have
these names. The runtime invoke the pluginobject using
positional (not keyword) arguments.

The ``event`` parameter is a ``modipyd.monitor.Event`` instance
which encapsulatesthe notification event fired by
``modipyd.monitor.Monitor`` instance. An eventobject has two
properties, ``type`` and ``descriptor``. The ``type``
propertyrepresents event type which is one of (created,
modified, removed). The ``descriptor``property is
``modipyd.descriptor.ModuleDescriptor`` instance which
encapsulatesmodified module information (See each class
documentations for more details).

The ``monitor`` parameter is a ``modipyd.monitor.Monitor``
instance which managesmonitoring modules and scheduling run
loop. The plugin can query monitoring modules,or stop run loop
by using Monitor object.

The ``context`` parameter is a dictionary object, containing
auxiliary variables.The plugin object is allowed to modify the
dictionary in any way it desires.
When called by the runtime, the plugin object can return (but
not required)a callable object. It is called with no arguments

.. NOTE::
    Sorry I'm not a native speaker, many parts of this documentation are
    borrowed heavily from `PEP 333`_ documentation...

.. _PEP 333: http://www.python.org/dev/peps/pep-0333/

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""


# ----------------------------------------------------------------
# Example Plugins
# ----------------------------------------------------------------
# pylint: disable-msg=W0613
def simple_plugin(event, monitor, context):
    """Simplest possible plugin object"""
    print "Event occurred:", event.type
    print "Modified module:", event.descriptor

class SimplePlugin(object):
    """Produce the same output, but using a class"""

    def __init__(self, event, monitor, context):
        self.event = event

    def __call__(self):
        print "Event occurred:", self.event.type
        print "Modified module:", self.event.descriptor


# ----------------------------------------------------------------
# Autotest Plugin
# ----------------------------------------------------------------
import os
import sys
import logging
import unittest
from modipyd import LOGGER
from modipyd.analysis import has_subclass


class Autotest(object):
    """
    Runs tests based on modules changed, and its dependencies.

    Options specified by context:
    ------------------------------------------------
        :autotest.test_runner: 
            The qualified name of ``unittest.TestRunner`` class
            (default is unittest.TextTestRunner)
    """

    # The qualified name of ``unittest.TestRunner`` class
    CONTEXT_TEST_RUNNER = 'autotest.test_runner'

    def __init__(self, event, monitor, context):
        self.descriptor = event.descriptor
        self.test_runner = context.get(Autotest.CONTEXT_TEST_RUNNER)

    def __call__(self):

        # Walking dependency graph in imported module to
        # module imports order.
        testables = []
        for desc in self.descriptor.walk_dependency_graph(reverse=True):
            LOGGER.info("-> Affected: %s" % desc.name)
            if has_subclass(desc, unittest.TestCase):
                LOGGER.debug("-> unittest.TestCase detected: %s" % desc.name)
                testables.append(desc)

        # Runntine tests
        if testables:
            # We can reload affected modules manually and run
            # all TestCase in same process. Running another process,
            # however, is simple and perfect solution.
            if LOGGER.isEnabledFor(logging.INFO):
                desc = ', '.join([x.name for x in testables])
                LOGGER.info("Running UnitTests: %s" % desc)
            # Propagates the level of modipyd.LOGGER to
            # the unittest runner subprocess.
            extra = ['--loglevel', LOGGER.getEffectiveLevel()];
            self.spawn_unittest_runner(testables, extra)

    def spawn_unittest_runner(self, testables, extra_arguments=None):
        """Spawn test runner process"""
        args = [sys.executable, '-m', 'modipyd.tools.unittest_runner']
        if extra_arguments:
            args.extend(extra_arguments)
        if self.test_runner:
            args.extend(['-r', self.test_runner])
        for t in testables:
            args.append(t.name)

        args = [str(arg) for arg in args]
        if sys.platform == "win32":
            # Avoid argument parsing problem in
            # windows, DOS platform
            args = ['"%s"' % arg for arg in args]

        LOGGER.debug("Spawn test runner process: %s" % ' '.join(args))
        return os.spawnve(os.P_WAIT, sys.executable, args, os.environ.copy())
