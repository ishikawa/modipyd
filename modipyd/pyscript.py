"""
The ``PyScript`` class is Python script file abstraction.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import os


class PyScript(object):
    """Python source code file"""

    def __init__(self, filename):
        if not os.path.isabs(filename):
            raise RuntimeError("filename must be absolute path: %s" % filename)

        self.filename = filename
        # Instance variable ``mtime`` will be updated by ``update()``
        self.mtime = None
        self.update()
        assert self.mtime is not None

    def update(self):
        """Return ``True`` if updated"""
        return self.update_mtime()

    def update_mtime(self):
        """Update modification time and return ``True`` if modified"""
        try:
            mtime = os.path.getmtime(self.filename)
            return self.mtime is None or mtime > self.mtime
        finally:
            self.mtime = mtime

    def __hash__(self):
        return hash(self.filename)

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
            self.filename == other.filename)

    def __str__(self):
        return self.filename


