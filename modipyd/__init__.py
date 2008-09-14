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
    if not os.path.exists(filepath):
        raise IOError(ENOENT, "No such file or directory", filepath)
    return []
