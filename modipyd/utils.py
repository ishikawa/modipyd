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
    except os.error:
        return False
    else:
        return (stat.S_ISREG(st.st_mode) and
            PYTHON_SCRIPT_FILENAME_RE.match(filepath))


def detect_modulename(filepath, search_path=None):
    """
    Try to detect the module name from *filepath* on
    the search path ``search_path``. If *path* is omitted or ``None``,
    ``sys.path`` is used.
    """
    dirpath, modname = os.path.split(filepath)
    if not modname:
        raise RuntimeError("filepath must not be directory")

    # ignore extention (e.g. '.py', '.pyc')
    modname, _ = os.path.splitext(modname)
    if modname == '__init__':
        # package itself
        dirpath, modname = os.path.split(dirpath)

    # Now, dirpath should be in sys.path so that
    # interpreter finds this module.
    import sys
    assert dirpath

    if search_path is None:
        search_path = sys.path

    for path in search_path:
        if dirpath.startswith(path):
            while dirpath != path:
                dirpath, parent = os.path.split(dirpath)
                modname = "%s.%s" % (parent, modname)
            return modname
    return None


def make_modulename(filepath):
    """
    Convert filepath so that it can be suitable
    for module name
    """
    # - Extract filename (without file extention)
    # - Make start with "_"
    # - Append sha1 hexdigest value
    # - Replace identifier character with safe character
    filename, _ = os.path.splitext(os.path.basename(filepath))
    try:
        import hashlib
        digest = hashlib.sha1(filepath).hexdigest()
    except ImportError:
        # < Python 2.5
        import sha
        digest = sha.new(filepath).hexdigest()

    modulename = "_".join(['', filename, digest])
    return re.sub(r'[^a-zA-Z0-9_]', '_', modulename)
