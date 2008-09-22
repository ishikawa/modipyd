"""
This module provides ``ModuleNameResolver`` class

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import os
import sys


class ModuleNameResolver(object):
    """Module Name Resolver"""

    def __init__(self, search_paths=None):
        """
        The ``search_paths`` argument is module search path,
        if *search_paths* is omitted or ``None``, ``sys.path`` is used.
        ``sys.path`` is used.
        """
        # search_paths would be modified, copy it.
        self.search_paths = (search_paths or sys.path)[:]

    def resolve(self, filepath):
        """
        Resolve the module name from *filepath* on search_paths.
        """
        from os.path import abspath, samestat
        from modipyd.utils import python_module_file, python_package

        if not python_module_file(filepath):
            raise RuntimeError("Not a python script: %s" % filepath)

        def splitmodname(filepath):
            # filepath must be absolute.
            filepath = os.path.abspath(filepath)
            dirpath, modname = os.path.split(filepath)
            assert os.path.isabs(dirpath) and modname

            # ignore extention (e.g. '.py', '.pyc')
            modname, _ = os.path.splitext(modname)
            assert _
            return dirpath, modname

        # Searching...
        skipped_name = None
        dirpath, modname = splitmodname(filepath)
        for syspath in (abspath(f) for f in self.search_paths):

            assert isinstance(syspath, basestring)
            if not os.path.isdir(syspath):
                # Only search in directory (ignore .zip, .egg, ...)
                continue

            st = os.stat(syspath)
            d, name = dirpath, modname

            while not samestat(st, os.stat(d)):
                if not python_package(d):
                    # encountered not a package
                    break
                if d == '/':
                    # not found in search path
                    break
                d, parent = os.path.split(d)
                name = '.'.join((parent, name))
            else:
                if python_package(dirpath) and '.' not in name:
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
                    skipped_name = name
                    continue

                if name.endswith(".__init__"):
                    # Remove tail '.__init__'
                    name = name[:-9]
                return name

        if skipped_name is not None:
            return skipped_name
        else:
            raise ImportError("No module name found: %s" % filepath)
