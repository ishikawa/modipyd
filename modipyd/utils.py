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


def find_modulename(filepath, search_paths=None):
    """
    Try to detect the module name from *filepath* on
    the search path ``search_paths``. If *path* is omitted or ``None``,
    ``sys.path`` is used.

    Notes: This function only returns first found module name.
    """
    from os.path import abspath, isabs, samestat
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

        st = os.stat(search_path)
        while not samestat(st, os.stat(dirpath)):
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
    return None
