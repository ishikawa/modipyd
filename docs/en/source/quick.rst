.. _quick:

Getting started with Modipyd and Autotest tool
=================================================

You can read :ref:`install` document, if you don't install *Modipyd* yet.

Basic Example
-------------
Suppose you have two ``.py`` files.::

  [~/examples/widget]
  % ls
  test_widget.py	widget.py

The file named ``widget.py`` is a normal Python script. On the other hand, ``test_widget.py`` is a test case  includes :class:`unittest.TestCase` subclasses.

``widget.py``:

.. literalinclude:: ../../../examples/widget/widget.py

``test_widget.py``:

.. literalinclude:: ../../../examples/widget/test_widget.py

You can start monitoring modification by executing :command:`pyautotest` (:option:``-v`` option is applied only for debugging)::

  % pyautotest -v
  [INFO] Loading plugin: <class 'modipyd.application.plugins.Autotest'> 
  [INFO] Loading BytecodeProcesser 'modipyd.bytecode.ImportProcessor' 
  [INFO] Loading BytecodeProcesser 'modipyd.bytecode.ClassDefinitionProcessor' 
  [INFO] Monitoring:
  test_widget: /Users/ishikawa/Developer/Workspace/Modipyd/modipyd/examples/widget/test_widget.py
    Dependencies: ['widget']
    Reverse: []
  widget: /Users/ishikawa/Developer/Workspace/Modipyd/modipyd/examples/widget/widget.py
    Dependencies: []
    Reverse: ['test_widget'] 

As output message mentioned above, :file:`widget.py` and :file:`test_widget.py` are now monitored by :command:`pyautotest`.
