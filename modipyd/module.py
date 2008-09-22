"""
Python module representation.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""


def find_source_and_compiled(filepath):
    from os.path import exists, splitext

    filename, _ = splitext(filepath)
    py_path = pyc_path = None

    path = ''.join([filename, '.pyo'])
    if exists(path):
        pyc_path = path
    else:
        path = ''.join([filename, '.pyc'])
        if exists(path):
            pyc_path = path

    path = ''.join([filename, '.py'])
    if exists(path):
        py_path = path

    return py_path, pyc_path


class Module(object):
    """Python module representation"""

    def __init__(self, modulename, filepath, code=None):
        super(Module, self).__init__()
        self.name = modulename
        self.filepath = filepath
        self.code = code

    def __str__(self):
        return "<module '%s' (%s)>" % (self.name, self.filepath)

    def compile(self):
        py_path, pyc_path = find_source_and_compiled(self.filepath)

        if pyc_path:
            # Attempt to load compiled bytecode.
            import marshal
            import imp

            fp = open(pyc_path, 'rb')
            try:
                try:
                    if fp.read(4) != imp.get_magic():
                        raise ImportError, "Bad magic number in %s" % filepath
                    fp.read(4)
                    self.code = marshal.load(fp)
                except:
                    # ignore, try to compile .py
                    pass
            finally:
                fp.close()

        if not self.code and py_path:
            # line endings must be represented by a single newline character ('\n'),
            # and the input must be terminated by at least one newline character.
            fp = open(py_path, 'U')
            try:
                self.code = compile(fp.read() + '\n', py_path, 'exec')
            finally:
                fp.close()


def collect_python_module_files(root):
    """Generates [.py, .pyc, .pyo]"""
    from modipyd import utils
    from os.path import splitext

    modules = {}
    for filepath in utils.collect_files(root, r'(?:\..+|CVS)$'):
        path, ext = splitext(filepath)

        # For performance gain, use bitmask value
        # instead of filepath string.
        modules.setdefault(path, 0)
        if ext == '.py':
            modules[path] += 1
        elif ext == '.pyc':
            modules[path] += 2
        elif ext == '.pyo':
            modules[path] += 4

    for path, mask in modules.iteritems():
        yield path, mask


if __name__ == '__main__':
    import os
    import sys
    import pprint
    from os.path import split, splitext
    #pprint.pprint(sys.path)

    sys.path.insert(0, os.getcwd())
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from modipyd import utils

    for path, mask in collect_python_module_files('.'):
        print path, mask
