"""
Python module representation.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import array
import dis
import sys
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
IMPORT_FROM = dis.opname.index('IMPORT_FROM')
IMPORT_STAR = dis.opname.index('IMPORT_STAR')

STORE_NAME = dis.opname.index('STORE_NAME')
STORE_GLOBAL = dis.opname.index('STORE_GLOBAL')
STORE_OPS = [STORE_NAME, STORE_GLOBAL]

BUILD_CLASS = dis.opname.index('BUILD_CLASS')
BUILD_TUPLE = dis.opname.index('BUILD_TUPLE')

POP_TOP = dis.opname.index('POP_TOP')

DEBUG = False

def _print(*args):
    for s in args:
        sys.stderr.write(str(s))
        sys.stderr.write(' ')
    sys.stderr.write('\n')

def _code_iter(co):
    code = array.array('B', co.co_code)
    return iter(code)

def _read_argc(op, code_iter):
    # opcodes which take arguments
    argc = 0
    if op >= dis.HAVE_ARGUMENT:
        argc += code_iter.next()
        argc += (code_iter.next() * 256)
    return argc


class ImportDisasm(object):
    """
    The disassembler for ``import`` statements

    ImportDisasm.imports attribute is a list such as:

        [(symbol, fully qualified)]

        e.g.
        import os
        --> [('os', 'os')]
        import os.path
        --> [('os.path', 'os.path')]
        from os.path import join as os_path_join
        --> [('os_path_join', 'os.path.join')]

    >>> disasm = ImportDisasm(compile(
    ...     'import os', '<string>', 'exec'))
    >>> disasm.scan()[0]
    ('os', 'os')

    >>> disasm = ImportDisasm(compile(
    ...     'import os.path', '<string>', 'exec'))
    >>> disasm.scan()[0]
    ('os.path', 'os.path')

    >>> disasm = ImportDisasm(compile(
    ...     'import os.path as os_path', '<string>', 'exec'))
    >>> disasm.scan()[0]
    ('os_path', 'os.path')

    """

    def __init__(self, co):
        self.co = co

        self.import_name = None
        self.fromlist = []
        self.has_star = False

        # Fully Qualified Name ::= '.'.join(self.fqn)
        # Access Name ::= Symbol + '.' + '.'.join(self.fqn[self.store:])
        self.fqn = self.store = None

        # value stacks
        self.consts = []

        # ``import``s
        self.imports = []

    def scan(self):
        code_iter = _code_iter(self.co)

        del self.imports[:]
        for op in code_iter:
            argc = _read_argc(op, code_iter)
            self.track(op, argc)
        return self.imports

    def track(self, op, argc):
        if LOAD_CONST == op:
            # An ``IMPORT_NAME`` is always preceded by a 2 ``LOAD_CONST``s,
            # they are:
            #
            #   (1) The level of relative imports
            #   (2) A tuple of "from" names, or None for regular import.
            #       The tuple may contain "*" for "from <mod> import *"
            self.consts.append(self.co.co_consts[argc])
        elif LOAD_ATTR == op:
            # import os.path as os_path
            # ...
            #  6 IMPORT_NAME              0 (os.path)
            #  9 LOAD_ATTR                1 (path)
            # 12 STORE_NAME               2 (os_path)
            # ...
            attr = self.co.co_names[argc]
            
            if self.import_name and self.store < len(self.fqn):
                assert self.fqn[self.store] == attr
                self.store += 1

        elif IMPORT_NAME == op:
            assert len(self.consts) >= 2
            self.import_name = self.co.co_names[argc]
            self.fqn = self.import_name.split('.')
            self.store = 1
        elif IMPORT_FROM == op:
            assert self.import_name
            self.fromlist.append(self.co.co_names[argc])
        elif IMPORT_STAR == op:
            assert self.import_name
            self.has_star = True
        elif STORE_NAME == op:
            self.store_name(self.co.co_names[argc])
        elif POP_TOP == op:
            self.clear_states()

    def clear_states(self):
        del self.fromlist[:]
        self.import_name = None
        self.fqn = self.store = None

    def store_name(self, name):
        if self.import_name and not self.fromlist:
            symbol = self.fqn[self.store:]
            symbol.insert(0, name)
            self.imports.append(('.'.join(symbol), '.'.join(self.fqn)))
            self.clear_states()


# pylint: disable-msg=C0321
def scan_code(co, module):
    if DEBUG: _print("scan_code: %s" % co.co_filename)

    assert co and module
    code_iter = _code_iter(co)
    fromlist = None
    values = []
    bases = None

    for op in code_iter:
        #if DEBUG: print dis.opname[op], argc
        argc = _read_argc(op, code_iter)

        # imports
        if LOAD_CONST == op:
            # An IMPORT_NAME is always preceded by a LOAD_CONST, it's
            # a tuple of "from" names, or None for a regular import.
            # The tuple may contain "*" for "from <mod> import *"
            fromlist = co.co_consts[argc]
        elif IMPORT_NAME == op:
            assert fromlist is None or type(fromlist) is tuple
            name = co.co_names[argc]
            module.imports.append((name, fromlist or ()))

        # classdefs
        if LOAD_NAME == op:
            if DEBUG: _print('LOAD_NAME %s' % co.co_names[argc])
            values.append(co.co_names[argc])
        elif LOAD_ATTR == op:
            if DEBUG: _print('LOAD_ATTR %s' % co.co_names[argc])
            if values and isinstance(values[-1], basestring):
                values[-1] = "%s.%s" % (values[-1], co.co_names[argc])
        elif BUILD_TUPLE == op:
            if DEBUG: _print(argc, values)

            # Because ``scan_code`` does not fully support
            # python bytecode spec, stack can be illegal.
            if len(values) >= argc:
                values[-argc:] = [tuple(values[-argc:])]
                if DEBUG: _print('BUILD_TUPLE', argc, values[-1])

        elif BUILD_CLASS == op:
            if values and isinstance(values[-1], tuple):
                bases = values.pop()
            else:
                bases = ()
            if DEBUG: _print('BUILD_CLASS', bases)
        elif STORE_NAME == op:
            if bases is not None:
                assert isinstance(bases, tuple)
                name = co.co_names[argc]
                module.classdefs.append((name, bases))
                if DEBUG:
                    _print("class %s%s:" % (name, str(bases)))
                bases = None
                del values[:]

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
        >>> modcode.filename
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
        self.classdefs = []
        scan_code(self.code, self)

    def __str__(self):
        return "<module '%s' (%s)>" % (self.name, self.filename)

    def __eq__(self, other):
        return (self is other or
                    (isinstance(other, type(self)) and
                     self.name == other.name))

    def __hash__(self):
        return hash(self.name)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
