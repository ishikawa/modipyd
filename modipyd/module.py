"""
Python module representation.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import dis
from modipyd import utils, LOGGER


# ----------------------------------------------------------------
# Loading, Compiling source code
# ----------------------------------------------------------------
def load_compiled(filepath):
    """
    Load and initialize a byte-compiled code file and return
    its ``code`` object. Return ``None`` if loading is failed.
    """
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
            LOGGER.warn(
                "Can't load compiled .pyc file: %s" % filepath,
                exc_info=True)
    finally:
        fp.close()

def compile_source(filepath):
    """
    Compile the source file at *filepath* into a code object.
    Code objects can be executed by an exec statement or
    evaluated by a call to ``eval()``.
    """
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
LOAD_NAME = dis.opname.index('LOAD_NAME')
LOAD_ATTR = dis.opname.index('LOAD_ATTR')

IMPORT_NAME = dis.opname.index('IMPORT_NAME')

STORE_NAME = dis.opname.index('STORE_NAME')
STORE_GLOBAL = dis.opname.index('STORE_GLOBAL')
STORE_OPS = [STORE_NAME, STORE_GLOBAL]

BUILD_CLASS = dis.opname.index('BUILD_CLASS')
BUILD_TUPLE = dis.opname.index('BUILD_TUPLE')


def scan_code(co, module):
    assert co and module
    code = co.co_code
    n, i = len(code), 0

    fromlist = None

    stack = []
    baseclasses = None

    while i < n:
        c = code[i]
        i += 1
        op = ord(c)

        # opcodes which take arguments
        if op >= dis.HAVE_ARGUMENT:
            oparg = ord(code[i]) + ord(code[i+1])*256
            i += 2

        # imports
        if LOAD_CONST == op:
            # An IMPORT_NAME is always preceded by a LOAD_CONST, it's
            # a tuple of "from" names, or None for a regular import.
            # The tuple may contain "*" for "from <mod> import *"
            fromlist = co.co_consts[oparg]
        elif IMPORT_NAME == op:
            assert fromlist is None or type(fromlist) is tuple
            name = co.co_names[oparg]
            module.imports.append((name, fromlist or ()))

        # classdefs
        else:
            if LOAD_NAME == op:
                #print 'LOAD_NAME', co.co_names[oparg]
                del stack[:]
                stack.append(co.co_names[oparg])
            elif LOAD_ATTR == op:
                #print 'LOAD_ATTR', co.co_names[oparg]
                if stack and isinstance(stack[-1], basestring):
                    stack[-1] = "%s.%s" % (stack[-1], co.co_names[oparg])
            elif BUILD_TUPLE == op:
                #print 'BUILD_TUPLE', oparg
                stack[-oparg:] = [tuple(stack[-oparg:])]
            elif BUILD_CLASS == op:
                #print 'BUILD_CLASS'
                if stack and isinstance(stack[-1], tuple):
                    baseclasses = stack.pop()
                else:
                    baseclasses = ()
            elif STORE_NAME == op and baseclasses:
                assert isinstance(baseclasses, tuple)
                #print "class %s : %s:" % (co.co_names[oparg],
                #                          ','.join(baseclasses))
                module.classdefs[co.co_names[oparg]] = baseclasses
                baseclasses = None
                del stack[:]

    for c in co.co_consts:
        if isinstance(c, type(co)):
            scan_code(c, module)


# ----------------------------------------------------------------
# Python Module Finder
# ----------------------------------------------------------------
# Bit masks for collect_module_code_files
PYTHON_SOURCE_MASK    = 1
PYTHON_COMPILED_MASK  = 2
PYTHON_OPTIMIZED_MASK = 4

def _collect_module_code_files(filepath_or_list):
    """Generates (filepath without extention, bitmask)"""
    from os.path import splitext

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

    return (item for item in modules.iteritems() if item[1] > 0)


def collect_module_code(filepath_or_list, search_path=None):
    for path, typebits in _collect_module_code_files(filepath_or_list):
        # Since changing .py file is not reflected by .pyc, .pyo quickly,
        # the plain .py file takes first prioriry.
        code = None

        if typebits & PYTHON_SOURCE_MASK:
            # .py
            sourcepath = path + '.py'
            code = compile_source(sourcepath)
        elif typebits & (PYTHON_OPTIMIZED_MASK | PYTHON_COMPILED_MASK):
            # .pyc, .pyo
            if typebits & PYTHON_OPTIMIZED_MASK:
                sourcepath = path + '.pyo'
            else:
                sourcepath = path + '.pyc'
            code = load_compiled(sourcepath)
        if not code:
            LOGGER.info("Couldn't load file at %s" % sourcepath)
            continue

        # module name
        try:
            modname = utils.resolve_modulename(sourcepath, search_path)
        except ImportError:
            LOGGER.info("Couldn't import file at %s, ignore" % sourcepath)
        else:
            yield ModuleCode(modname, sourcepath, code)

def read_module_code(filepath, search_path=None):
    if not isinstance(filepath, basestring):
        raise TypeError("The filepath argument "
            "must be instance of basestring, but was "
            "instance of %s" % type(filepath))

    g = collect_module_code(filepath, search_path)
    try:
        module = g.next()
    except StopIteration:
        raise ImportError("Can't import %s" % filepath)
    else:
        try:
            g.next()
        except StopIteration:
            pass
        else:
            raise RuntimeError("Multiple module instance at %s" % filepath)
        return module


# ----------------------------------------------------------------
# Module class
# ----------------------------------------------------------------
class ModuleCode(object):
    """Python module representation"""

    def __init__(self, modulename, filename, code):
        """
        Instanciates and initialize ``ModuleCode`` object

        >>> code = compile("import os; import sys", '<string>', 'exec')
        >>> code is not None
        True
        >>> modcode = ModuleCode('__main__', code.co_filename, code)
        >>> modcode.name
        '__main__'
        >>> modcode.filepath
        '<string>'
        >>> len(modcode.imports)
        2
        >>> modcode.imports[0][0]
        'os'
        >>> modcode.imports[1][0]
        'sys'
        """
        super(ModuleCode, self).__init__()
        self.name = modulename
        self.filename = filename
        self.code = code

        self.imports = []
        self.classdefs = {}
        scan_code(self.code, self)

    def __str__(self):
        return "<module '%s' (%s)>" % (self.name, self.filename)

    def __eq__(self, other):
        return (self is other or
                    (isinstance(other, type(self)) and
                     self.name == other.name))

    def __hash__(self):
        return hash(self.name)

    @property
    def filepath(self):
        return self.filename


if __name__ == "__main__":
    import doctest
    doctest.testmod()
