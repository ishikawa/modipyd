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
from errno import ENOENT


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
