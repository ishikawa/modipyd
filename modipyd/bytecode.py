"""
Modipyd BytecodeProcessor Architecture
================================================

This module provides a interface of Modypyd Bytecode processor,
``BytecodeProcessor`` and standard processors.
You can install your own processors by adding processor name
into ``modipyd.BYTECODE_PROCESSORS`` variable.

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""

import array
import dis
from modipyd import HAS_RELATIVE_IMPORTS


# ----------------------------------------------------------------
# Opcode
# ----------------------------------------------------------------
LOAD_CONST = dis.opname.index('LOAD_CONST')
LOAD_NAME = dis.opname.index('LOAD_NAME')
LOAD_ATTR = dis.opname.index('LOAD_ATTR')

IMPORT_NAME = dis.opname.index('IMPORT_NAME')
IMPORT_FROM = dis.opname.index('IMPORT_FROM')
IMPORT_STAR = dis.opname.index('IMPORT_STAR')

STORE_NAME = dis.opname.index('STORE_NAME')
STORE_FAST = dis.opname.index('STORE_FAST')
STORE_DEREF = dis.opname.index('STORE_DEREF')

BUILD_CLASS = dis.opname.index('BUILD_CLASS')
BUILD_TUPLE = dis.opname.index('BUILD_TUPLE')

POP_TOP = dis.opname.index('POP_TOP')


# ----------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------
def code_iter(co):
    code = array.array('B', co.co_code)
    return iter(code)

def read_argc(op, it):
    # opcodes which take arguments
    argc = 0
    if op >= dis.HAVE_ARGUMENT:
        argc += it.next()
        argc += (it.next() * 256)
    return argc

def _scan_code(co, processor, context):
    # print "scan_code: %s" % co.co_filename
    assert co and context is not None
    code_it = code_iter(co)
    processor.enter(co)
    for op in code_it:
        # print dis.opname[op], argc
        argc = read_argc(op, code_it)
        processor.process(op, argc, co)
    processor.exit(co)

    for c in co.co_consts:
        if isinstance(c, type(co)):
            _scan_code(c, processor, context)

def scan_code(co, processor, context):
    _scan_code(co, processor, context)
    processor.populate(context)


# ----------------------------------------------------------------
# Bytecode Processor Interface
# ----------------------------------------------------------------
class BytecodeProcessor(object):
    """
    The ``BytecodeProcessor`` disassembles the bytecode and
    populates properties of the bytecode into context object.
    """

    def __init__(self):
        super(BytecodeProcessor, self).__init__()

    def enter(self, co):
        pass

    def exit(self, co):
        pass

    def process(self, op, argc, co):
        pass

    def populate(self, context):
        """
        Populate properties of the bytecode into *context* object.
        *context* object need to be substitutable for dictionaries.
        """
        pass


# ----------------------------------------------------------------
# Bytecode Processor Chain
# ----------------------------------------------------------------
class ChainedBytecodeProcessor(BytecodeProcessor):

    def __init__(self, processores):
        super(ChainedBytecodeProcessor, self).__init__()
        self.processores = list(processores)

    def enter(self, co):
        for processor in self.processores:
            processor.enter(co)

    def process(self, op, argc, co):
        for processor in self.processores:
            processor.process(op, argc, co)

    def exit(self, co):
        for processor in self.processores:
            processor.exit(co)

    def populate(self, context):
        for processor in self.processores:
            processor.populate(context)


# ----------------------------------------------------------------
# Standard Processors
# ----------------------------------------------------------------

class ImportProcessor(BytecodeProcessor):

    def __init__(self):
        super(ImportProcessor, self).__init__()

        self.import_name = None
        self.fromname = None

        # Fully Qualified Name ::= '.'.join(self.fqn)
        # Access Name ::= Symbol + '.' + '.'.join(self.fqn[self.store:])
        self.fqn = self.store = None

        # value stacks
        self.consts = []

        # ``import``s
        self.imports = []

    def enter(self, co):
        pass

    def exit(self, co):
        pass

    def process(self, op, argc, co):
        if LOAD_CONST == op:
            # An ``IMPORT_NAME`` is always preceded by a 2 ``LOAD_CONST``s,
            # they are:
            #
            #   (1) The level of relative imports
            #   (2) A tuple of "from" names, or None for regular import.
            #       The tuple may contain "*" for "from <mod> import *"
            #print "LOAD_CONST", co.co_consts[argc]
            self.consts.append(co.co_consts[argc])
        elif LOAD_ATTR == op:
            # import os.path as os_path
            # ...
            #  6 IMPORT_NAME              0 (os.path)
            #  9 LOAD_ATTR                1 (path)
            # 12 STORE_NAME               2 (os_path)
            # ...
            attr = co.co_names[argc]
            #print "LOAD_CONST", attr
            if self.import_name and self.store < len(self.fqn):
                assert self.fqn[self.store] == attr, \
                    "LOAD_ATTR '%s' must equal to '%s' in %s (at %s)" % \
                        (attr, self.fqn[self.store],
                         str(self.fqn),
                         co.co_filename)
                self.store += 1

        elif IMPORT_NAME == op:
            #print "IMPORT_NAME", co.co_names[argc]
            assert len(self.consts) >= 1
            self.import_name = co.co_names[argc]
            self.fqn = self.import_name.split('.')
            self.store = 1
        elif IMPORT_FROM == op:
            # import_name is an empty string in ``from .+ import ``
            assert self.import_name is not None
            self.fromname = co.co_names[argc]
        elif IMPORT_STAR == op:
            assert self.import_name
            # ::= "from" module "import" "*"
            #
            # from ... import * is currently not fully supported
            #self.has_star = True
            self.fromname = '*'
            self.store_name('*')
            self.clear_states()

        elif STORE_NAME == op:
            #print "STORE_NAME", co.co_names[argc]
            self.store_name(co.co_names[argc])
        elif STORE_FAST == op:
            #print "STORE_FAST", co.co_varnames[argc]
            self.store_name(co.co_varnames[argc])
        elif STORE_DEREF == op:
            #print "STORE_DEREF", co.co_cellvars[argc]
            self.store_name(co.co_cellvars[argc])

        elif POP_TOP == op:
            self.clear_states()

    def clear_states(self):
        self.import_name = self.fromname = None
        self.fqn = self.store = None
        del self.consts[:]

    def store_name(self, name):
        # import_name is an empty string in
        # ``from .+ import `` statement
        if self.import_name is None:
            return

        # The Absolute and Relative Imports future has been
        # implemented in Python 2.5
        #
        # http://docs.python.org/whatsnew/pep-328.html
        level = -1
        assert len(self.consts) >= 1
        if HAS_RELATIVE_IMPORTS:
            assert len(self.consts) >= 2
            level = self.consts[-2]
            assert level >= -1, \
                "import level is illegal: %s (%s)" % \
                (str(level), str(self.consts))

        if not self.fromname:
            # import ...
            symbol = self.fqn[self.store:]
            symbol.insert(0, name)
            self.imports.append(('.'.join(symbol), '.'.join(self.fqn), level))
            #print "-> import %s" % str(self.imports[-1])
            self.clear_states()
        else:
            # from ... import ...

            # import_name is an empty string in
            # ``from .+ import `` statement
            if self.import_name:
                fqn = '.'.join(self.fqn + [self.fromname])
            else:
                fqn = self.fromname
            self.imports.append((name, fqn, level))
            #print "-> import %s" % str(self.imports[-1])
            self.fromname = None

    def populate(self, context):
        imports = context.setdefault('imports', [])
        imports.extend(self.imports)


class ClassDefinitionProcessor(BytecodeProcessor):

    def __init__(self):
        super(ClassDefinitionProcessor, self).__init__()
        self.classdefs = []
        self.values = []
        self.bases = None

    def enter(self, co):
        pass

    def exit(self, co):
        pass

    def process(self, op, argc, co):
        values = self.values

        if LOAD_NAME == op:
            # print 'LOAD_NAME %s' % co.co_names[argc]
            values.append(co.co_names[argc])
        elif LOAD_ATTR == op:
            # print 'LOAD_ATTR %s' % co.co_names[argc]
            if values and isinstance(values[-1], basestring):
                values[-1] = "%s.%s" % (values[-1], co.co_names[argc])
        elif BUILD_TUPLE == op:
            # print argc, values

            # Because ``scan_code`` does not fully support
            # python bytecode spec, stack can be illegal.
            if len(values) >= argc:
                values[-argc:] = [tuple(values[-argc:])]
                # print 'BUILD_TUPLE', argc, values[-1]

        elif BUILD_CLASS == op:
            if values and isinstance(values[-1], tuple):
                self.bases = values.pop()
            else:
                self.bases = ()
            # print 'BUILD_CLASS', bases
        elif STORE_NAME == op:
            bases = self.bases
            if bases is not None:
                assert isinstance(bases, tuple)
                name = co.co_names[argc]
                self.classdefs.append((name, bases))
                # print "class %s%s:" % (name, str(bases))
                self.bases = None
                del values[:]

    def populate(self, context):
        classdefs = context.setdefault('classdefs', [])
        classdefs.extend(self.classdefs)
