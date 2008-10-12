.. _quick:

Getting started with Modipyd and Autotest tool
=================================================

You can read :ref:`install` document, if you don't install *Modipyd* yet.

Basic Example: The :class:`Widget` class
----------------------------------------------------
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
----------------------------------------------------
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
-----------------------------------------------------------------------

You have three assignment statements in :func:`Widget.__init__`, assigns function arguments to instance variables. You can perform multiple assignment using tuples.

:file:`widget.py`:

.. literalinclude:: ../../../examples/widget/001/widget.py

When you edit :file:`widget.py`, :command:`pyautotest` automatically reloads modified module (:file:`widget.py`), and then, automatically runs all dependent testcase (:file:`test_widget.py`).::

  [INFO] Reload module descriptor 'widget' at widget.py 
  [INFO] Modified: widget: widget.py
    Dependencies: []
    Reverse: ['test_widget'] 
  [INFO] -> Affected: widget 
  [INFO] -> Affected: test_widget 
  [INFO] Running UnitTests: test_widget 
  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.000s

  OK

Adding :func:`resize` method
----------------------------------------------------

You decide to add :func:`Widget.resize` method. The :func:`Widget.resize` takes two arguments ``width`` and ``height``, then change the region with new rectangle. Along with test driven development, you write a test  before the :func:`Widget.resize` implementation.

:file:`test_widget.py`:

.. literalinclude:: ../../../examples/widget/002/test_widget.py

This test must inevitably fail because :func:`Widget.resize` is missing. This validates that the test harness is working correctly and that the test does not mistakenly pass without requiring any new code. In addition, :command:`pyautotest` correctly finds new test case and its dependencies.

::

  ======================================================================
  ERROR: test_resize (test_widget.WidgetResizeTestCase)
  ----------------------------------------------------------------------
  Traceback (most recent call last):
    File "test_widget.py", line 21, in test_resize
      widget.resize(45, 50)
  AttributeError: 'Widget' object has no attribute 'resize'

  ----------------------------------------------------------------------
  Ran 3 tests in 0.001s

So you can begin to write :func:`Widget.resize` code.

:file:`widget.py`:

.. literalinclude:: ../../../examples/widget/002/widget.py

Now all test cases pass.

::

  [INFO] Running UnitTests: test_widget 
  ...
  ----------------------------------------------------------------------
  Ran 3 tests in 0.000s

  OK

