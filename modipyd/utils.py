"""
Utilities

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""
import os
import re
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
    pass

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


# Python script filename pattern
PYTHON_SCRIPT_FILENAME_RE = re.compile(r'^.*\.py[co]?$')

def is_python_module_file(filepath):
    """
    Return ``True`` if *filepath* is Python script/bytecode
    (".py", ".pyc", ".pyo").
    """
    try:
        st = os.stat(filepath)
    except (TypeError, os.error):
        return False
    else:
        return (stat.S_ISREG(st.st_mode) and
            PYTHON_SCRIPT_FILENAME_RE.match(filepath))

def is_python_package(dirpath):
    from os.path import isdir, isfile, join
    if not isdir(dirpath):
        return False
    return (isfile(join(dirpath, '__init__.py')) or
            isfile(join(dirpath, '__init__.pyc')) or
            isfile(join(dirpath, '__init__.pyo')))

# ----------------------------------------------------------------
# find_modulename
# ----------------------------------------------------------------
def find_modulename(filepath, search_paths=None):
    """
    Try to detect the module name from *filepath* on
    the search path ``search_paths``. If *path* is omitted or ``None``,
    ``sys.path`` is used.

    Notes: This function only returns first found module name.
    """
    from os.path import abspath, samestat
    if not is_python_module_file(filepath):
        raise RuntimeError("Not a python script: %s" % filepath)

    # filepath must be absolute.
    filepath = os.path.abspath(filepath)
    dirpath, modname = os.path.split(filepath)
    assert os.path.isabs(dirpath) and modname

    # ignore extention (e.g. '.py', '.pyc')
    modname, _ = os.path.splitext(modname)
    assert _

    # Now, dirpath should be in search path so that
    # interpreter finds this module.
    if search_paths is None:
        import sys
        search_paths = sys.path

    def _find_modulename(name, dirpath, search_path):
        # search_path must be string
        assert isinstance(search_path, basestring)
        if not os.path.isdir(search_path):
            return None

        qp = is_python_package(dirpath)
        st = os.stat(search_path)
        while not samestat(st, os.stat(dirpath)):
            if not qp:
                return None # No parent package
            if dirpath == '/':
                return None # not found in search_path
            dirpath, parent = os.path.split(dirpath)
            name = "%s.%s" % (parent, name)
        else:
            if name.endswith(".__init__"):
                name = name[:-9]
        return name

    for syspath in (abspath(f) for f in search_paths):
        name = _find_modulename(modname, dirpath, syspath)
        if name:
            return name
    raise ImportError("No module name found: %s" % filepath)
