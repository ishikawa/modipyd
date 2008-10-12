.. _quick:

Getting started with Modipyd and Autotest tool
=================================================

You can read :ref:`install` document, if you don't install *Modipyd* yet.

Basic Example
-------------
Suppose you have two ``.py`` files.::

  [~/modipyd/examples/widget]
  % ls
  test_widget.py	widget.py

The file named ``widget.py`` is a normal Python script. On the other hand, ``test_widget.py`` is a test case  includes :class:`unittest.TestCase` subclasses.

``widget.py``:

.. literalinclude:: ../../../examples/widget/000/widget.py

``test_widget.py``:

.. literalinclude:: ../../../examples/widget/000/test_widget.py

Running pyautotest
~~~~~~~~~~~~~~~~~~
You can start monitoring modification by executing :command:`pyautotest` (The \ :option:``-v`` option is specified so that :command:`pyautotest` prints debugging messages)::

  % pyautotest -v
  [INFO] Loading plugin: <class 'modipyd.application.plugins.Autotest'> 
  [INFO] Loading BytecodeProcesser 'modipyd.bytecode.ImportProcessor' 
  [INFO] Loading BytecodeProcesser 'modipyd.bytecode.ClassDefinitionProcessor' 
  [INFO] Monitoring:
  test_widget: test_widget.py
    Dependencies: ['widget']
    Reverse: []
  widget: widget.py
    Dependencies: []
    Reverse: ['test_widget'] 

As output message mentioned above, the :command:`pyautotest` tool is now monitoring :file:`widget.py` and :file:`test_widget.py`.

Refactoring: Assigning multiple values at once in intialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


