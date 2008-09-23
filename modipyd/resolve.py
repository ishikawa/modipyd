"""
This module provides ``ModuleNameResolver`` class

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import os
import sys
from os.path import isdir, abspath, expanduser
from modipyd import utils


def _normalize_path(filepath):
    #return realpath(abspath(expanduser(filepath)))
    return abspath(expanduser(filepath))

def _split_module_name(filepath):
    """
    /path/to/module.py -> '/path/to/', 'module'
    """
    # filepath must be absolute.
    dirpath, modname = os.path.split(filepath)
    assert os.path.isabs(dirpath) and modname

    # ignore extention (e.g. '.py', '.pyc')
    modname, _ = os.path.splitext(modname)
    assert _
    return dirpath, modname

class ModuleNameResolver(object):
    """Module Name Resolver"""

    def __init__(self, search_paths=None):
        """
        The ``search_paths`` argument is module search path,
        if *search_paths* is omitted or ``None``, ``sys.path`` is used.
        ``sys.path`` is used.
        """
        # Cofigure module search path (copy it)
        syspaths = (search_paths or sys.path)
        self.search_paths = [_normalize_path(d) for d in syspaths if isdir(d)]
        for d in self.search_paths:
            assert isinstance(d, basestring)
            assert isdir(d)

        # caches
        self.cache_package = {}

    def python_package(self, directory):
        p = self.cache_package.get(directory)
        if p is None:
            p = utils.python_package(directory)
            self.cache_package[directory] = p
        return p

    def resolve(self, filepath):
        """
        Resolve the module name from *filepath* on search_paths.
        """

        if not filepath:
            raise RuntimeError("Empty string passed")

        filepath = _normalize_path(filepath)
        if not utils.python_module_file(filepath):
            raise RuntimeError("Not a python script: %s" % filepath)

        # Searching...
        skipped_name = None
        dirpath, modname = _split_module_name(filepath)
        for syspath in self.search_paths:

            d, name = dirpath, [modname]
            # Because paths is normalized,
            # fast string comparison is sufficient
            while not d == syspath:
                if not self.python_package(d):
                    # encountered not a package
                    break
                if d == '/':
                    # not found in search path
                    break
                d, parent = os.path.split(d)
                name.insert(0, parent)
            else:
                level = len(name)
                assert level > 0

                if self.python_package(dirpath) and level < 2:
                    # script is created under a package,
                    # but its module name is not a package.
                    #
                    # For example, consider:
                    #
                    #   src/packageA/__init__.py
                    #               /a.py
                    #
                    # and *sys.path* is:
                    #
                    #   ['src/packageA', 'src']
                    #
                    # a.py is in src/packageA, so module name 'a' is
                    # matched. But better module name is 'packageA.a'
                    # because a.py is created under the package
                    # 'packageA'.
                    #
                    # Store result name, and continues with
                    # the next iteration of the **for** loop.
                    skipped_name = name[0]
                    continue

                if level > 1 and name[-1] == '__init__':
                    # Remove tail '__init__'
                    del name[-1]
                return '.'.join(name)

        if skipped_name is not None:
            return skipped_name
        else:
            raise ImportError("No module name found: %s" % filepath)
