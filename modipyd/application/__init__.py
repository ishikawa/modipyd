"""
Generic modipyd application

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

from modipyd import LOGGER
from modipyd.utils import import_component
from modipyd.monitor import Event, Monitor


TYPE_STRINGS = dict(
    zip(Event.TYPES, ('Modified', 'Created', 'Removed')))

class Application(object):

    def __init__(self, paths):
        self.paths = paths
        self.plugins = []

    def install_plugin(self, plugin):
        """
        Install a plugin specified by *plugin*. The *plugin* argument
        must be callable object (e.g. function, class) or a qualified
        name of the plugin itself.

        Read the ``modipyd.application.plugins`` module documentation
        for the plugin architecture details.
        """

        if isinstance(plugin, basestring):
            try:
                plugin = import_component(plugin)
            except (ImportError, AttributeError):
                LOGGER.error("Loading plugin '%s' failed" % plugin)
                raise

        if not callable(plugin):
            raise TypeError("The plugin must be callable object")

        if hasattr(plugin, 'func_code'):
            LOGGER.info("Installed plugin: %s" % plugin.func_code.co_name)
        else:
            LOGGER.info("Installed plugin: %s" % plugin)

        self.plugins.append(plugin)

    def invoke_plugins(self, event, monitor):
        context = {}
        for plugin in self.plugins:
            try:
                ret = plugin(event, monitor, context)
                # the plugin object can return (but not required)
                # a callable object. It is called with no arguments
                if callable(ret):
                    ret()
            except StandardError:
                LOGGER.warn(
                    "Exception occurred while invoking plugin",
                    exc_info=True)

    def run(self):
        monitor = Monitor(self.paths)
        for event in monitor.start():
            LOGGER.info("%s: %s" % (TYPE_STRINGS[event.type],
                event.descriptor.describe(indent=4)))
            self.invoke_plugins(event, monitor)
