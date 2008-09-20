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


def detect_modulename(filepath, search_paths=None):
    """
    Try to detect the module name from *filepath* on
    the search path ``search_paths``. If *path* is omitted or ``None``,
    ``sys.path`` is used.
    
    Notes: This function only returns first found module name.
    """
    if not is_python_module_file(filepath):
        raise RuntimeError("Not a python script: %s" % filepath)

    # filepath must be absolute.
    filepath = os.path.abspath(filepath)
    dirpath, modname = os.path.split(filepath)
    assert modname

    # ignore extention (e.g. '.py', '.pyc')
    modname, _ = os.path.splitext(modname)
    assert _

    # Now, dirpath should be in search path so that
    # interpreter finds this module.
    if search_paths is None:
        import sys
        search_paths = sys.path

    def is_parent_or_same(test_dir, filepath):
        assert test_dir and filepath
        assert os.path.isabs(test_dir) and os.path.isabs(filepath)
        
        # 1. /path/to/parent - /path/to/parent
        # 2. /path/to/parent/ - /path/to/parent/file
        # 3. /path/to/parent - /path/to/parent/file
        return (filepath.startswith(test_dir) and (
            len(filepath) == len(test_dir) or
            test_dir[-1] == '/' or
            filepath[len(test_dir)] == '/'))

    def detect(name, dirpath, search_paths):
        assert name and dirpath
        assert os.path.isabs(dirpath)
        assert dirpath[-1] != '/'

        for path in search_paths:

            path = os.path.abspath(path)
            if not is_parent_or_same(path, dirpath):
                continue

            while dirpath != path:
                dirpath, parent = os.path.split(dirpath)
                assert parent, "parent is empty, leads infinite loop!"
                name = "%s.%s" % (parent, name)
            else:
                if name.endswith(".__init__"):
                    name = name[:-9]
            yield name

    for detected in detect(modname, dirpath, search_paths):
        return detected
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
