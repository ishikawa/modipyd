"""
Modipyd: Autotest for Python, and more
=======================================

**Modipyd** is a `Python`_ module dependency analysis and monitoring
modification framework, written by Takanori Ishikawa and licensed
under `the MIT license`_.

**This project aims to provide:**

* Automated testing tool **pyautotest** (like `ZenTest's autotest <http://
www.zenspider.com/ZSS/Products/ZenTest/>`_) for Python
* *Plugin architecture* designed to be simple enough to allow user to customize 
action triggered by the module modification event
* API for *Bytecode analysis*, *Module dependency analysis*, and *Monitoring 
module modification*

    :copyright: 2008-2010 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.

.. _Python: http://www.python.org/
.. _the MIT license: http://www.opensource.org/licenses/mit-license.php
"""

__version__ = '1.1'
__author__ = 'Takanori Ishikawa <takanori.ishikawa@gmail.com>'
__url__ = 'http://www.metareal.org/p/modipyd/'
__license__ = 'MIT License'
__docformat__ = 'restructuredtext'

__all__ = ['LOGGER', 'HAS_RELATIVE_IMPORTS', 'BYTECODE_PROCESSORS']


import os
import sys


# ----------------------------------------------------------------
# Logger
# ----------------------------------------------------------------
def __configure_logger():
    """Configure project-wide logger"""
    import logging
    handler = logging.StreamHandler()

    handler.setFormatter(logging.Formatter(
        '[%(levelname)s] %(message)s '))
    # Fully descriptive format
    #handler.setFormatter(logging.Formatter(
    #    '%(asctime)s [%(levelname)s] %(message)s '
    #    '(File "%(pathname)s", line %(lineno)d)'))

    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    # If a line below is uncommented, LOGGER's level is accidentally
    # changed when this module is reloaded
    #logger.setLevel(logging.WARN)
    return logger

# Logger object for project
LOGGER = __configure_logger()


# ----------------------------------------------------------------
# Python version compatibility
# ----------------------------------------------------------------
# The Absolute and Relative Imports has been implemented in Python 2.5
# http://docs.python.org/whatsnew/pep-328.html
HAS_RELATIVE_IMPORTS = (sys.hexversion >= 0x2050000)


# ----------------------------------------------------------------
# Bytecode Processors
# ----------------------------------------------------------------
# The modipyd.bytecode.BytecodeProcessor subclasses 
# for disassembling bytecode, and populating properties.
#
# See modipyd.bytecode.BytecodeProcessor class and standard
# processorsfor for more details.
#
BYTECODE_PROCESSORS = [
    # Standard processors
    'modipyd.bytecode.ImportProcessor',
    'modipyd.bytecode.ClassDefinitionProcessor',
]
