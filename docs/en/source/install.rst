.. _install:

How to install Modipyd
====================================
Before you can use *Modipyd*, you'll need to get it installed. This document describes how to install Modipyd.

Prerequisites
-----------------------------------
Modipyd requires **Python version 2.4** or higher. No other libraries/modules are needed.

Get Python at `http://www.python.org <http://www.python.org>`_. If you're running Linux or Mac OS X, you probably already have it installed.

Installing the latest release
---------------------------------------------------
1. Download the latest release (zip_ or `tar.gz`_ release available).
2. Unpack the downloaded file (e.g. ``unzip ishikawa-modipyd-XXX.zip`` for zip archive or ``tar xzvf ishikawa-modipyd-XXX.tar.gz`` for tar.gz archive).
3. Change into the directory created in step 2 (e.g. ``cd ishikawa-modipyd-XXX``).
4. Enter the command ``sudo python setup.py install`` at the shell prompt.

These commands will install:

* :mod:`modipyd` package in your Python installation's :file:`site-packages` directory
* :command:`modipyd`, :command:`pyautotest` commands in platform-specific location (e.g. :file:`/usr/local/bin`).

That's all. You can now move onto :ref:`quick`.

.. _zip: http://github.com/ishikawa/modipyd/zipball/release-1-0
.. _tar.gz: http://github.com/ishikawa/modipyd/tarball/release-1-0
