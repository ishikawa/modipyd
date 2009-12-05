"""
This module provides an interface to the mechanisms
used to resolve module name from mofule filepath.

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""

import os
import sys
from os.path import isdir, abspath, expanduser, basename
from modipyd import utils


def normalize_path(filepath):
    """Normalize path name"""
    #return os.path.realpath(abspath(expanduser(filepath)))
    return abspath(expanduser(filepath))

def script_filename_to_modulename(filepath):
    try:
        import hashlib
        digest = hashlib.sha1(filepath).hexdigest()
    except ImportError:
        import sha
        digest = sha.new(filepath).hexdigest()
    name = basename(filepath).replace('.', '_')
    name = '_'.join((name, digest))
    return name


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
        syspaths = utils.wrap_sequence(syspaths)
        assert isinstance(syspaths, (list, tuple))

        self.search_paths = [normalize_path(d) for d in syspaths if isdir(d)]
        for d in self.search_paths:
            assert isinstance(d, basestring)
            assert isdir(d)

        # caches
        self.cache_package    = {}
        self.cache_script_mod = {}

    def python_package(self, directory):
        try:
            return self.cache_package[directory]
        except KeyError:
            name = utils.python_package(directory)
            self.cache_package[directory] = name
            return name

    def script_filename_to_modulename(self, filepath):
        try:
            return self.cache_script_mod[filepath]
        except KeyError:
            name = script_filename_to_modulename(filepath)
            self.cache_script_mod[filepath] = name
            return name

    def resolve(self, filepath):
        """
        Resolve the module name from *filepath* on search_paths.
        Return (module name, package name), if the module is not
        in a package, package name is ``None``.
        """
        if not filepath:
            raise ImportError("filepath is empty")

        filepath = normalize_path(filepath)
        if not utils.python_module_file(filepath):
            raise ImportError("Not a python script: %s" % filepath)

        modname, package = self._resolve(filepath)

        if not package:
            # The file located at filepath is a script (not in a package).
            # For avoiding name collision with other packages, scripts,
            # rename with the SHA1 hash value of its filepath.
            modname = self.script_filename_to_modulename(filepath)

        return modname, package

    def _resolve(self, filepath):
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
