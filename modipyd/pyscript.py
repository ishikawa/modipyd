"""
The ``PyScript`` class is Python script file abstraction.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import os
import sys


class PyScript(object):
    """Python source code file"""

    def __init__(self, filename):
        if not os.path.isabs(filename):
            raise RuntimeError("filename must be absolute path: %s" % filename)
        if not os.path.exists(filename):
            raise RuntimeError("No such file or directory: %s" % filename)

        self.filename = filename
        # Instance variables will be initialized by ``update()``
        self.mtime = self.module = None
        self.update()
        assert self.mtime is not None

    def update(self):
        """Return ``True`` if updated"""
        if self.update_mtime():
            self.load_module()
            return True
        else:
            return False

    def load_module(self, reload_module=False):
        from modipyd.utils import find_modulename, import_module
        try:
            modname = find_modulename(self.filename)
            
            self.module = import_module(modname)
            assert self.module
            if reload_module:
                reload(self.module)
        except ImportError:
            raise

    def update_mtime(self):
        """Update modification time and return ``True`` if modified"""
        mtime = None
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


