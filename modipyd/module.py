"""
Python module representation.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import os
import sys
import dis


# ----------------------------------------------------------------
# Loading, Compiling source code
# ----------------------------------------------------------------
def load_compiled(filepath):
    import marshal
    import imp
    fp = open(filepath, 'rb')
    try:
        try:
            if fp.read(4) != imp.get_magic():
                raise ImportError, "Bad magic number in %s" % filepath
            fp.read(4)
            return marshal.load(fp)
        except StandardError:
            # ignore, try to compile .py
            from modipyd import LOGGER
            LOGGER.warn(
                "Can't load compiled .pyc file: %s" % filepath,
                exc_info=True)
    finally:
        fp.close()

def compile_source(filepath):
    # line endings must be represented by a single newline character ('\n'),
    # and the input must be terminated by at least one newline character.
    fp = open(filepath, 'U')
    try:
        return compile(fp.read() + '\n', filepath, 'exec')
    finally:
        fp.close()


# ----------------------------------------------------------------
# Bytecode analysis
# ----------------------------------------------------------------
LOAD_CONST = dis.opname.index('LOAD_CONST')
IMPORT_NAME = dis.opname.index('IMPORT_NAME')
STORE_NAME = dis.opname.index('STORE_NAME')
STORE_GLOBAL = dis.opname.index('STORE_GLOBAL')
STORE_OPS = [STORE_NAME, STORE_GLOBAL]

def scan_code(co, module):
    assert co and module
    code = co.co_code
    n, i = len(code), 0
    fromlist = None
    while i < n:
        c = code[i]
        i = i+1
        op = ord(c)
        if op >= dis.HAVE_ARGUMENT:
            oparg = ord(code[i]) + ord(code[i+1])*256
            i = i+2
        if op == LOAD_CONST:
            # An IMPORT_NAME is always preceded by a LOAD_CONST, it's
            # a tuple of "from" names, or None for a regular import.
            # The tuple may contain "*" for "from <mod> import *"
            fromlist = co.co_consts[oparg]
        elif op == IMPORT_NAME:
            assert fromlist is None or type(fromlist) is tuple
            name = co.co_names[oparg]
            module.imports.append((name, fromlist or ()))
    for c in co.co_consts:
        if isinstance(c, type(co)):
            scan_code(c, module)


# ----------------------------------------------------------------
# Python Module Finder
# ----------------------------------------------------------------
# Bit masks for collect_python_module_files
PYTHON_SOURCE_MASK    = 1
PYTHON_COMPILED_MASK  = 2
PYTHON_OPTIMIZED_MASK = 4

def _collect_python_module_files(filepath_or_list):
    """Generates (filepath without extention, bitmask)"""
    from os.path import splitext
    from modipyd import utils

    modules = {}
    for filepath in utils.collect_files(filepath_or_list, ['.?*', 'CVS']):
        path, ext = splitext(filepath)

        # For performance gain, use bitmask value
        # instead of filepath string.
        modules.setdefault(path, 0)
        if ext == '.py':
            modules[path] |= PYTHON_SOURCE_MASK
        elif ext == '.pyc':
            modules[path] |= PYTHON_COMPILED_MASK
        elif ext == '.pyo':
            modules[path] |= PYTHON_OPTIMIZED_MASK

    for path, bitmask in modules.iteritems():
        if bitmask > 0:
            yield path, bitmask


def collect_python_module(filepath_or_list, search_path=None):
    from modipyd import utils
    for path, typebits in _collect_python_module_files(filepath_or_list):

        # ,pyc, .pyo
        code = None
        if typebits & (PYTHON_OPTIMIZED_MASK | PYTHON_COMPILED_MASK):

            if typebits & PYTHON_OPTIMIZED_MASK:
                sourcepath = path + '.pyo'
            else:
                sourcepath = path + '.pyc'
            code = load_compiled(sourcepath)

        # .py
        if not code and typebits & PYTHON_SOURCE_MASK:
            sourcepath = path + '.py'
            code = compile_source(sourcepath)

        if not code:
            continue

        # module name
        try:
            modname = utils.find_modulename(sourcepath, search_path)
        except ImportError:
            continue
        else:
            yield Module(modname, sourcepath, code)


# ----------------------------------------------------------------
# Module class
# ----------------------------------------------------------------
class Module(object):
    """Python module representation"""

    def __init__(self, modulename, filepath, code):
        super(Module, self).__init__()
        self.name = modulename
        self.filepath = filepath
        self.code = code

        self.imports = []
        scan_code(self.code, self)

    def __str__(self):
        return "<module '%s' (%s)>" % (self.name, self.filepath)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.getcwd())
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    args = sys.argv[1:]
    for m in collect_python_module(args or '.'):
        print m
        print m.imports
