"""
This module provides an interface to the mechanisms
used to resolve module name from module filepath.

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""

import os
import sys
import imp
import os.path
from os.path import abspath, expanduser
from modipyd import utils


def normalize_path(filepath):
    """Normalize path name"""
    return abspath(expanduser(filepath))

def resolve_relative_modulename(modulename, package, level):
    if level <= 0:
        return modulename
    else:
        for _ in xrange(1, level):
            package = package[:package.rindex('.')]

        return '.'.join((package, modulename))

class ModuleNameResolver(object):
    """
    This class provides an interface to the mechanisms
    used to resolve module name from a python source file path.
    """

    def __init__(self, search_paths=None):
        """
        The ``search_paths`` argument is module search path,
        if *search_paths* is omitted or ``None``, ``sys.path`` is used.
        """
        super(ModuleNameResolver, self).__init__()

        # Cofigure module search path (copy it)
        syspaths = (search_paths or sys.path)
        syspaths = utils.sequence(syspaths)
        self.search_paths = [normalize_path(d) for d in syspaths if os.path.isdir(d)]

        # caches
        self.cache_package     = {}
        self.cache_find_module = {}

    def python_package(self, directory):
        try:
            return self.cache_package[directory]
        except KeyError:
            package = utils.python_package(directory)
            self.cache_package[directory] = package
            return package


    def _find_module(self, modname, path):
        kind = imp.PY_SOURCE
        names = []

        for name in modname.split('.'):
            names.append(name)
            key = '.'.join(names)

            try:
                pathname, kind = self.cache_find_module[key]

                if kind != imp.PKG_DIRECTORY and key != modname:
                    self.cache_find_module[key] = (None, None)
                    raise ImportError, "No module named %s" % modname

            except KeyError:
                module_path = utils.sequence(path, copy=list)
                try:
                    fp, pathname, description = imp.find_module(names[-1], module_path)
                    if fp:
                        fp.close()
                    kind = description[2]
                    self.cache_find_module[key] = (pathname, kind)
                except ImportError:
                    self.cache_find_module[key] = (None, None)
                    raise

            if pathname is None and kind is None:
                raise ImportError, "No module named %s" % modname

            path = pathname

        return pathname, kind


    def resolve(self, filepath):
        """
        Resolves the name of the module located at *filepath*.
        If successful, returns names of module and package.
        """
        modname, package = self._resolve(filepath)
        if modname:
            # validates resolved module name with imp.find_module
            pathname, kind = self._find_module(modname, self.search_paths)

            if kind == imp.PKG_DIRECTORY:
                pathname = os.path.join(pathname, '__init__.py')

            pt1, _ = os.path.splitext(normalize_path(filepath))
            pt2, _ = os.path.splitext(normalize_path(pathname))

            if pt1 != pt2:
                raise ImportError("Can't resolve module name: %s" % filepath)

        return modname, package

    def _resolve(self, filepath):

        if not filepath:
            raise ImportError("filepath is empty")

        filepath = normalize_path(filepath)

        if not os.path.exists(filepath):
            raise ImportError, "No such file or directory found at %s" % filepath
        if not utils.python_module_file(filepath):
            raise ImportError, "Not a python script at %s" % filepath

        # Searching...
        #
        # split path components
        # ignore extention (e.g. '.py', '.pyc')
        dirpath, modname = os.path.split(filepath)
        modname, _ = os.path.splitext(modname)

        skipped_name = None
        package_name = None
        compiled_forms = [(dirpath, [modname])]

        for syspath in self.search_paths:

            i = 0
            while not compiled_forms[i][0] == syspath:
                # compile
                i += 1
                if i == len(compiled_forms):
                    d, names = compiled_forms[i-1]

                    # Encountered not a package, or not found in
                    # the module search path
                    if not self.python_package(d) or d == '/':
                        break

                    names = names[:] # copy
                    d, parent = os.path.split(d)
                    names.insert(0, parent)

                    compiled_forms.append((d, names))
            else:
                d, names = compiled_forms[i]
                if self.python_package(dirpath):
                    package_name = '.'.join(names[:-1])
                else:
                    package_name = None

                if i == 0:
                    if self.python_package(d):
                        # script is created under a package,
                        # but its module name is not a package style
                        # (e.g. 'package.module').
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
                        skipped_name = names[0]
                        package_name = None
                        continue
                else:
                    if names[-1] == '__init__':
                        # The package initialization module.
                        # Remove tail '__init__'
                        del names[-1]

                return '.'.join(names), package_name

        if skipped_name is not None:
            return skipped_name, package_name
        else:
            raise ImportError("No module name found: %s" % filepath)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
