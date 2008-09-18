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
import re
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
LOGGER = __configure_logger(logging.WARN)


# ----------------------------------------------------------------
# Public APIs
# ----------------------------------------------------------------
def collect_files(filepath_or_list):
    """
    ``collect_files()`` generates the file names in a directory tree.
    Note: ``collect_files()`` will not visit symbolic links to
    subdirectories.
    """
    for filepath in wrap_sequence(filepath_or_list):
        if not os.path.exists(filepath):
            raise IOError(ENOENT, "No such file or directory", filepath)
        elif not os.path.isdir(filepath):
            yield filepath
        else:
            # pylint: disable-msg=W0612
            for dirpath, dirnames, filenames in os.walk(filepath):
                for filename in filenames:
                    yield os.path.join(dirpath, filename)

def wrap_sequence(obj, sequence_type=tuple):
    """
    Return a tuple whose item is obj.
    If obj is already a list or tuple, it is returned unchanged.
    """
    if isinstance(obj, (list, tuple)):
        return obj
    else:
        return sequence_type((obj,))

def make_modulename(filepath):
    """Convert string (e.g. filepath) so that it can be suitable for module name"""
    # - Remove file extention
    # - Replace identifier character with safe character
    # - Make start with "_"
    path, ext = os.path.splitext(filepath)
    return '_' + re.sub(r'[^a-zA-Z0-9_]', '_', path)
