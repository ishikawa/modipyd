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
    # - Remove file extention
    # - Replace identifier character with safe character
    # - Make start with "_"
    path, _ = os.path.splitext(filepath)
    return '_' + re.sub(r'[^a-zA-Z0-9_]', '_', path)
