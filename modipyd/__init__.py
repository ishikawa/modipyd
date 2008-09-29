"""
modipyd
================================================

How this software works:

1. Generating python module dependency graphs
2. Monitoring module (file) modification
3. Notifying modified and dependent modules

So I named it modipyd (modified + python).

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

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
        '%(asctime)s [%(levelname)s] %(message)s '
        '(File "%(pathname)s", line %(lineno)d)'))
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
# The Absolute and Relative Imports has been
# implemented in Python 2.5
#
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
