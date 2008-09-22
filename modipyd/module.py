"""
Python module representation.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""


class Module(object):
    """Python module representation"""

    def __init__(self, modulename, filepath, code=None):
        super(Module, self).__init__()
        self.name = modulename
        self.filepath = filepath
        self.code = code

    def __str__(self):
        return "<module '%s' (%s)>" % (self.name, self.filepath)

if __name__ == '__main__':
    import os
    import sys
    import pprint
    from os.path import split, splitext
    #pprint.pprint(sys.path)

    sys.path.insert(0, os.getcwd())
    from modipyd import utils

    for f in utils.collect_files('.'):
        if not utils.python_source_file(f):
            continue
        
        try:
            modname = utils.find_modulename(f)
        except ImportError:
            pass
        else:
            print modname, f
