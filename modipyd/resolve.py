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
    The ModuleNameResolver class provides the interface to
    the mechanism of resolving a fully qualified module name
    from a its source filepath.
    """

    def __init__(self, path=None):
        """
        The ``path`` argument is module search path,
        if *path* is omitted or ``None``, ``sys.path`` is used.
        """
        super(ModuleNameResolver, self).__init__()

        # list of module search paths
        syspaths = (path or sys.path)
        syspaths = utils.sequence(syspaths)
        self.path = [normalize_path(d) for d in syspaths if os.path.isdir(d)]

        # caches
        self._cache_package     = {}
        self._cache_find_module = {}
        self._cache_resolve     = {}

    def _resolve_package(self, directory):
        try:
            return self._cache_package[directory]
        except KeyError:
            package = utils.python_package(directory)
            self._cache_package[directory] = package
            return package

    def _find_module(self, modname, path):
        try:
            pathname, kind = self._cache_find_module[modname]
        except KeyError:
            name = modname
            i = modname.rfind('.')
            if i != -1:
                path, _kind = self._find_module(modname[:i], path)
                name = modname[i+1:]
                if _kind != imp.PKG_DIRECTORY or not name:
                    self._cache_find_module[modname] = (None, None)
                    raise ImportError, "No module named %s" % modname
            try:
                fp, pathname, description = imp.find_module(name, utils.sequence(path, copy=list))
                if fp:
                    fp.close()
                kind = description[2]
                self._cache_find_module[modname] = (pathname, kind)
            except ImportError:
                    self._cache_find_module[modname] = (None, None)
                    raise
        else:
            if not pathname:
                raise ImportError, "No module named %s" % modname

        return pathname, kind

    def resolve(self, filepath):
        """
        Resolves the name of the module located at *filepath*.
        If successful, returns the name of the module and its package.
        """
        try:
            modname, package = self._cache_resolve[filepath]
        except KeyError:
            try:
                modname, package = self._resolve(filepath)
                if modname:
                    # validates resolved module name with imp.find_module
                    pathname, kind = self._find_module(modname, self.path)

                    if kind == imp.PKG_DIRECTORY:
                        pathname = os.path.join(pathname, '__init__.py')

                    pt1, _ = os.path.splitext(normalize_path(filepath))
                    pt2, _ = os.path.splitext(normalize_path(pathname))

                    if pt1 != pt2:
                        raise ImportError("Can't resolve module name: %s" % filepath)
            except ImportError:
                self._cache_resolve[filepath] = (None, None)
                raise
            else:
                self._cache_resolve[filepath] = (modname, package)
        else:
            if not modname:
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

        for syspath in self.path:

            i = 0
            while not compiled_forms[i][0] == syspath:
                # compile
                i += 1
                if i == len(compiled_forms):
                    d, names = compiled_forms[i-1]

                    # Encountered not a package, or not found in
                    # the module search path
                    if not self._resolve_package(d) or d == '/':
                        break

                    names = names[:] # copy
                    d, parent = os.path.split(d)
                    names.insert(0, parent)

                    compiled_forms.append((d, names))
            else:
                d, names = compiled_forms[i]
                if self._resolve_package(dirpath):
                    package_name = '.'.join(names[:-1])
                else:
                    package_name = None

                if i == 0:
                    if self._resolve_package(d):
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
