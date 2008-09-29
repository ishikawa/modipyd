"""
Python module code representation.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

from modipyd import utils, LOGGER, BYTECODE_PROCESSORS
from modipyd.resolve import ModuleNameResolver
from modipyd.utils.decorators import require
from modipyd import bytecode as bc


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
        if fp.read(4) != imp.get_magic():
            raise ImportError, "Bad magic number in %s" % filepath
        fp.read(4)
        return marshal.load(fp)
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
# Python Module Finder
# ----------------------------------------------------------------
# Bit masks for collect_module_code_files
PYTHON_SOURCE_MASK    = 1
PYTHON_COMPILED_MASK  = 2
PYTHON_OPTIMIZED_MASK = 4

# file extention -> typebits mask
PYTHON_FILE_TYPES = {
    '.py': PYTHON_SOURCE_MASK,
    '.pyc': PYTHON_COMPILED_MASK,
    '.pyo': PYTHON_OPTIMIZED_MASK,
}


@require(filename=basestring)
def module_file_typebits(filename):
    from os.path import splitext
    path, ext = splitext(filename)
    typebits = PYTHON_FILE_TYPES.get(ext, 0)
    return (path, ext, typebits)

def collect_python_module_file(filepath_or_list):
    """Generates (filepath without extention, bitmask)"""
    modules = {}
    for filepath in utils.collect_files(filepath_or_list, ['.?*', 'CVS']):
        # For performance gain, use bitmask value
        # instead of filepath string.
        path, _, typebits = module_file_typebits(filepath)
        modules.setdefault(path, 0)
        modules[path] |= typebits
    return (item for item in modules.iteritems() if item[1] > 0)

def collect_module_code(filepath_or_list, search_path=None):
    resolver = ModuleNameResolver(search_path)
    for filename, typebits in collect_python_module_file(filepath_or_list):
        # Since changing .py file is not reflected by .pyc, .pyo quickly,
        # the plain .py file takes first prioriry.
        try:
            yield read_module_code(filename,
                search_path=search_path, typebits=typebits,
                resolver=resolver, allow_compilation_failure=True)
        except ImportError:
            LOGGER.debug("Couldn't import file", exc_info=True)


@require(filename=basestring,
         typebits=(int, None),
         resolver=(ModuleNameResolver, None))
def read_module_code(filename, typebits=None, search_path=None,
        resolver=None,
        allow_compilation_failure=False):
    """
    Read python module file, and return ``ModuleCode`` instance.
    If *typebits* argument is not ``None``, *filename* must be
    filepath without file extention.
    If *typebits* argument is ``None``, it is detected by filename.
    """

    if typebits is None:
        filename, _, typebits = module_file_typebits(filename)
    if resolver is None:
        resolver = ModuleNameResolver(search_path)

    code = None
    try:
        if typebits & PYTHON_SOURCE_MASK:
            # .py
            sourcepath = filename + '.py'
            code = compile_source(sourcepath)
        elif typebits & (PYTHON_OPTIMIZED_MASK | PYTHON_COMPILED_MASK):
            # .pyc, .pyo
            if typebits & PYTHON_OPTIMIZED_MASK:
                sourcepath = filename + '.pyo'
            else:
                sourcepath = filename + '.pyc'
                code = load_compiled(sourcepath)
        else:
            assert False, "illegal typebits: %d" % typebits
    except (SyntaxError, ImportError):
        LOGGER.warn(
            "Exception occurred while loading compiled bytecode",
            exc_info=True)
        if not allow_compilation_failure:
            raise

    # Resolve module name, may raise ImportError
    module_name, package_name = resolver.resolve(sourcepath)
    return ModuleCode(module_name, package_name, sourcepath, code)


# ----------------------------------------------------------------
# Module class
# ----------------------------------------------------------------

# cached processor classes
BYTECODE_PROCESSORS_CACHE = []

def load_bytecode_processors():
    """
    Loading BytecodeProcessor from modipyd.BYTECODE_PROCESSORS
    settings. Return ChainedBytecodeProcessor instance holds
    all loaded processors.
    """
    if not BYTECODE_PROCESSORS_CACHE and BYTECODE_PROCESSORS:
        for name in BYTECODE_PROCESSORS:
            LOGGER.info("Loading BytecodeProcesser '%s'" % name)
            klass = utils.import_component(name)
            BYTECODE_PROCESSORS_CACHE.append(klass)

    processors = []
    for klass in BYTECODE_PROCESSORS_CACHE:
        processors.append(klass())
    return bc.ChainedBytecodeProcessor(processors)

class ModuleCode(object):
    """Python module representation"""

    def __init__(self, modulename, packagename, filename, code):
        """
        Instanciates and initialize ``ModuleCode`` object

        >>> code = compile(
        ...     "import os;"
        ...     "from os.path import join as join_path",
        ...     '<string>', 'exec')
        >>> modcode = ModuleCode('__main__', '', code.co_filename, code)
        >>> modcode.name
        '__main__'
        >>> modcode.filename
        '<string>'
        >>> imports = modcode.context['imports']
        >>> len(imports)
        2
        >>> imports[0]
        ('os', 'os', -1)
        >>> imports[1]
        ('join_path', 'os.path.join', -1)
        """
        super(ModuleCode, self).__init__()
        self.name = modulename
        self.package_name = packagename
        self.filename = filename
        self.context = {}

        if code is None:
            # Maybe source file contains SyntaxError?
            pass
        else:
            self.update_code(code)

    def update_code(self, co):
        self.context.clear()
        processor = load_bytecode_processors()
        bc.scan_code(co, processor, self.context)

    def reload(self, co=None):
        if co is None:
            f = self.filename

            if utils.python_source_file(f):
                co = compile_source(f)
            elif utils.python_compiled_file(f):
                co = load_compiled(f)
            else:
                raise ImportError("No module named %s at %s" % (self.name, f))

        self.update_code(co)
        return co

    def __str__(self):
        return "<ModuleCode '%s' (%s)>" % (self.name, self.filename)

    def __eq__(self, other):
        return (self is other or
                    (isinstance(other, type(self)) and
                     self.name == other.name))

    def __hash__(self):
        return hash(self.name)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
