"""
Utilities

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""
import os
import re
import sys
import stat


def wrap_sequence(obj, sequence_type=tuple):
    """
    Return a tuple whose item is obj.
    If obj is already a list or tuple, it is returned unchanged.
    """
    if isinstance(obj, (list, tuple)):
        return obj
    else:
        return sequence_type((obj,))

def compile_python_source(filepath, optimization=False):
    """
    Compile a source file to byte-code and write out
    the byte-code cache file. The source code is loaded
    from the file name *filepath*. The byte-code is cached
    in the normal manner (*filepath* + 'c' or 'o' if
    optimization is enabled).
    """
    from os import spawnv
    from sys import executable, platform

    args = [executable]
    if optimization:
        args.append('-O')
    args += ['-m', 'py_compile']

    if isinstance(filepath, (tuple, list)):
        args.extend(filepath)
    else:
        args.append(filepath)

    if platform == "win32":
        args = ['"%s"' % arg for arg in args]
    return spawnv(os.P_WAIT, executable, args)


# ----------------------------------------------------------------
# File browser
# ----------------------------------------------------------------
def collect_files(filepath_or_list, ignore_list=None):
    """
    ``collect_files()`` generates the file names in a directory tree.
    Note: ``collect_files()`` will not visit symbolic links to
    subdirectories. *ignore_list* argument is ignore filename patterns
    (using fnmatch).
    """
    import fnmatch

    def ignore(filename):
        if ignore_list:
            for pattern in ignore_list:
                if fnmatch.fnmatch(filename, pattern):
                    return True
        return False

    for filepath in wrap_sequence(filepath_or_list):

        if ignore(os.path.basename(filepath)):
            continue

        if not os.path.exists(filepath):
            from errno import ENOENT
            raise IOError(ENOENT, "No such file or directory", filepath)
        elif not os.path.isdir(filepath):
            yield filepath
        else:
            # pylint: disable-msg=W0612
            for dirpath, dirnames, filenames in os.walk(filepath):
                # For in-place deletion (avoids copying the list),
                # Don't delete anything earlier in the list than
                # the current element through.
                for i, dirname in enumerate(reversed(dirnames)):
                    if ignore(dirname):
                        # don't visit ignore directory
                        del dirnames[-(i+1)]
                for filename in filenames:
                    if not ignore(filename):
                        yield os.path.join(dirpath, filename)


# ----------------------------------------------------------------
# Path utilities
# ----------------------------------------------------------------
def python_module_file(filepath):
    """
    Return ``True`` if path is an existing Python source
    file (*.py*). This follows symbolic links.
    """
    return (python_source_file(filepath) or
            python_compiled_file(filepath))

def python_source_file(filepath):
    """
    Return ``True`` if path is an existing Python source
    file (*.py*). This follows symbolic links.
    """
    try:
        st = os.stat(filepath)
    except (TypeError, os.error):
        return False
    else:
        return (stat.S_ISREG(st.st_mode) and
                filepath.endswith('.py'))

def python_compiled_file(filepath):
    """
    Return ``True`` if path is an existing Python compiled
    bytecode file (*.pyc* or *.pyo*). This follows symbolic links.
    """
    try:
        st = os.stat(filepath)
    except (TypeError, os.error):
        return False
    else:
        return (stat.S_ISREG(st.st_mode) and
                   (filepath.endswith('.pyc') or
                    filepath.endswith('.pyo')))

def python_package(dirpath):
    """
    Return ``True`` if *dirpath* is an existing directory that is
    Python package directory (contains ``__init__.py[co]``).
    """
    from os.path import isdir
    return isdir(dirpath) and python_module_exists(dirpath, '__init__')

def python_module_exists(dirpath, modulename):
    """
    Return ``True`` if *dirpath* refers to an existing directory that
    contains Python module named *modulename*.
    """
    from os.path import isdir, isfile, join
    return (isdir(dirpath) and
                (isfile(join(dirpath, '%s.py' % modulename)) or
                 isfile(join(dirpath, '%s.pyc' % modulename)) or
                 isfile(join(dirpath, '%s.pyo' % modulename))))


# ----------------------------------------------------------------
# Working with modules
# ----------------------------------------------------------------
def import_module(modulename):
    """
    Return loaded module if module is already loaded in
    ``sys.modules``, otherwise load module and return it.
    """
    if modulename not in sys.modules:
        __import__(modulename)
    return sys.modules[modulename]

# TODO: ``find_modulename`` is major bottleneck of performance :-(
def find_modulename(filepath, search_paths=None):
    """
    Try to detect the module name from *filepath* on
    the search path ``search_paths``. If *path* is omitted or ``None``,
    ``sys.path`` is used.

    Notes: This function only returns first found module name.
    """
    from os.path import abspath, samestat
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

    # Now, dirpath should be in search path so that
    # interpreter finds this module.
    if search_paths is None:
        search_paths = sys.path

    # Searching...
    skipped_name = None
    dirpath, modname = splitmodname(filepath)
    for syspath in (abspath(f) for f in search_paths):

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
