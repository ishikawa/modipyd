1.1
-------

* Fixed `#9 pyautotest doesn't use module aliases`_ reported by Kevin Clark.
* Minor code cleanup.

1.1 rc1
-------

* Fixed module name collision problem. Suppose you have ``test`` package and ``test.py`` script in the same directory, Modipyd could not distinguish ``test`` and ``test.py``.
* Improved ``modipyd.monitor.Monitor``: tracking changes of files not in module search path.
* Improved ``modipyd.tools.unittest_runner``: search module by filepath instead of its name when the target is not in a package.
* Reduced execution of update dependencies.
* Propagates the level of modipyd.LOGGER to the unittest runner proces.
* Applied a patch contributed by Michael Opitz (`#7 Modules with mixed class-types`_)

.. _#7 Modules with mixed class-types: http://metareal.lighthouseapp.com/projects/17658/tickets/7-modules-with-mixed-class-types#ticket-7-1
.. _#9 pyautotest doesn't use module aliases: http://metareal.lighthouseapp.com/projects/17658-modipyd/tickets/9
