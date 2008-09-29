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
    
    class PluginClass:
        \"\"\"Provide same function, but using a class\"\"\"
    
        def __init__(self, event, monitor, context):
            self.event = event
    
        def __call__(self)
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

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

.. NOTE::
    Sorry I'm not a native speaker, many parts of this documentation are
    borrowed heavily from `PEP 333`_ documentation...

.. _PEP 333: http://www.python.org/dev/peps/pep-0333/
"""

# pylint: disable-msg=W0613
def simple_plugin(event, monitor, context):
    """Simplest possible plugin object"""
    print "Event occurred:", event.type
    print "Modified module:", event.descriptor
