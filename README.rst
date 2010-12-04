Modipyd: Autotest for Python, and more
======================================

Modipyd_ is a Python module dependency analysis and monitoring modifications framework, written by Takanori Ishikawa and licensed under the MIT license.

This project aims to provide

* Automated testing tool **pyautotest** (like `ZenTest's autotest`_) for Python
* Plugin architecture designed to be simple enough to allow user to customize action triggered by module modification events
* API for Bytecode analysis, Module dependency analysis, and Monitoring module modifications

Please visit `the project website`_ (Japanese version is here__) for more details.

Requirements
------------

Python 2.4 or higher

Developer Notes
---------------

``make lint`` runs pylint_ with a configuration file ``.pylintrc`` in top level directory.

Copyright
---------

Copyright (c) 2008-2009 **Takanori Ishikawa**, All rights reserved.

License
-------

The MIT license. See the LICENSE_ file for more details.

.. _Modipyd: http://www.metareal.org/p/modipyd/
.. _ModipydJa: http://www.metareal.org/p/modipyd/ja/
.. _the project website: Modipyd_
.. __: ModipydJa_
.. _ZenTest's autotest: http://www.zenspider.com/ZSS/Products/ZenTest/
.. _pylint: http://www.logilab.org/857
.. _LICENSE: http://github.com/ishikawa/modipyd/tree/master/LICENSE

