"""
Utilities

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""
import os
import sys
import stat

# pylint: disable-msg=W0401
# Make 'from modipyd.utils import OrderedSet' statement works
from modipyd.utils.ordered_set import *


def wrap_sequence(obj, sequence_type=tuple):
    """
    Return a tuple whose item is obj.
    If obj is already a list or tuple, it is returned unchanged.

    >>> wrap_sequence(None)[0] is None
    True
    >>> wrap_sequence("")
    ('',)
    >>> wrap_sequence([])
    []
    >>> wrap_sequence(())
    ()
    >>> wrap_sequence(123, sequence_type=list)
    [123]
    """
    if isinstance(obj, (list, tuple)):
        return obj
    else:
        return sequence_type((obj,))

def split_module_name(module_name):
    """
    >>> split_module_name('')
    ('', '')
    >>> split_module_name('module')
    ('', 'module')
    >>> split_module_name('module.a')
    ('module', 'a')
    >>> split_module_name('module.a.b')
    ('module.a', 'b')
    """
    i = module_name.rfind('.')
    if i == -1:
        return ('', module_name)
    else:
        return (module_name[:i], module_name[i+1:])

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
    # os.path.isdir() check is not needed
    return python_module_exists(dirpath, '__init__')

def python_module_exists(dirpath, modulename):
    """
    Return ``True`` if *dirpath* refers to an existing directory that
    contains Python module named *modulename*.
    """
    # os.path.isdir() check is not needed
    from os.path import isfile, join
    return (isfile(join(dirpath, '%s.py' % modulename)) or
                 isfile(join(dirpath, '%s.pyc' % modulename)) or
                 isfile(join(dirpath, '%s.pyo' % modulename)))


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

def import_component(name):
    """
    As a workaround for __import__ behavior,
    returns extract the desired component

    >>> import_component('os').__name__
    'os'
    >>> import types
    >>> type(import_component('os.path.join')) == types.FunctionType
    True
    """
    # Import component
    # As a workaround for __import__ behavior, 
    #   1. import module
    #   2. use getattr() to extract the desired component

    # 1. import module
    names = name.split('.')
    assert names and len(names) > 0
    if len(names) == 1:
        return __import__(names[0])

    try:
        modname = '.'.join(names[:-1])
        module = __import__(modname)
        for name in names[1:-1]:
            module = getattr(module, name)
    except ImportError:
        raise
    else:
        # 2. use getattr() to extract the desired component
        return getattr(module, names[-1])

def resolve_modulename(filepath, search_paths=None):
    """
    Try to detect the module name from *filepath* on
    the search path ``search_paths``. If *search_paths*
    is omitted or ``None``, ``sys.path`` is used.

    Notice: This function is provided for convenience.
    You should use ``modipyd.resolve.ModuleNameResolver``
    class for better performance.
    """
    from modipyd.resolve import ModuleNameResolver
    return ModuleNameResolver(search_paths).resolve(filepath)[0]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
