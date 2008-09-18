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


# ----------------------------------------------------------------
# Logger
# ----------------------------------------------------------------
def __configure_logger():
    """Configure project-wide logger"""
    import logging
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s '
        '(File "%(pathname)s", line %(lineno)d, in %(funcName)s)'))
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.WARN)
    return logger

# Logger object for project
LOGGER = __configure_logger()


# ----------------------------------------------------------------
# Public APIs
# ----------------------------------------------------------------
def collect_files(filepath_or_list):
    """
    ``collect_files()`` generates the file names in a directory tree.
    Note: ``collect_files()`` will not visit symbolic links to
    subdirectories.
    """
    from modipyd.utils import wrap_sequence
    for filepath in wrap_sequence(filepath_or_list):
        if not os.path.exists(filepath):
            from errno import ENOENT
            raise IOError(ENOENT, "No such file or directory", filepath)
        elif not os.path.isdir(filepath):
            yield filepath
        else:
            # pylint: disable-msg=W0612
            for dirpath, dirnames, filenames in os.walk(filepath):
                for filename in filenames:
                    yield os.path.join(dirpath, filename)
