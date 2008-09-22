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

