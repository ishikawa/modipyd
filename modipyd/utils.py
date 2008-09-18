"""
Utilities

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""
import os
import re


def wrap_sequence(obj, sequence_type=tuple):
    """
    Return a tuple whose item is obj.
    If obj is already a list or tuple, it is returned unchanged.
    """
    if isinstance(obj, (list, tuple)):
        return obj
    else:
        return sequence_type((obj,))

def make_modulename(filepath):
    """
    Convert string (e.g. filepath) so that it can be suitable
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
