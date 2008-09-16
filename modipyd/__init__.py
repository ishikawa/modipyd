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
import logging
from errno import ENOENT


# ----------------------------------------------------------------
# Logger
# ----------------------------------------------------------------
def __configure_logger(level):
    """Configure project-wide logger"""
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s '
        '(File "%(pathname)s", line %(lineno)d, in %(funcName)s)'))
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger

# Logger object for project
LOGGER = __configure_logger(logging.INFO)


# ----------------------------------------------------------------
# Public APIs
# ----------------------------------------------------------------
def collect_files(filepath):
    """``collect_files()`` generates the file names in a directory tree."""
    if not os.path.exists(filepath):
        raise IOError(ENOENT, "No such file or directory", filepath)
    elif not os.path.isdir(filepath):
        yield filepath
    else:
        # pylint: disable-msg=W0612
        for dirpath, dirnames, filenames in os.walk(filepath):
            for filename in filenames:
                yield os.path.join(dirpath, filename)
