"""
Python module representation.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import array
import dis


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


class ImportDisassembler(object):
    """
    The disassembler for ``import`` statements

    ImportDisassembler.imports attribute is a list such as:

        [(symbol, fully qualified, level)]

    *level*

    level specifies whether to use absolute or relative imports.
    The default is -1 which indicates both absolute and relative imports
    will be attempted. 0 means only perform absolute imports.
    Positive values for level indicate the number of parent directories
    to search relative to the directory of the module..

        e.g.
        import os
        --> [('os', 'os', -1)]
        import os.path
        --> [('os.path', 'os.path', -1)]
        from os.path import join as os_path_join
        --> [('os_path_join', 'os.path.join', -1)]

    >>> disasm = ImportDisassembler(compile(
    ...     'import os', '<string>', 'exec'))
    >>> disasm.scan()[0]
    ('os', 'os', -1)

    >>> disasm = ImportDisassembler(compile(
    ...     'import os.path', '<string>', 'exec'))
    >>> disasm.scan()[0]
    ('os.path', 'os.path', -1)

    >>> disasm = ImportDisassembler(compile(
    ...     'import os.path as os_path', '<string>', 'exec'))
    >>> disasm.scan()[0]
    ('os_path', 'os.path', -1)

    >>> disasm = ImportDisassembler(compile(
    ...     'from os import path', '<string>', 'exec'))
    >>> disasm.scan()[0]
    ('path', 'os.path', -1)

    >>> # from ... import * is currently not fully supported
    >>> disasm = ImportDisassembler(compile(
    ...     'from os.path import *', '<string>', 'exec'))
    >>> disasm.scan()[0]
    ('*', 'os.path.*', -1)
    """

    def __init__(self, co):
        self.co = co

        self.import_name = None
        self.fromname = None

        # Fully Qualified Name ::= '.'.join(self.fqn)
        # Access Name ::= Symbol + '.' + '.'.join(self.fqn[self.store:])
        self.fqn = self.store = None

        # value stacks
        self.consts = []

        # ``import``s
        self.imports = []

    def scan(self):
        code = code_iter(self.co)
        del self.imports[:]
        for op in code:
            argc = read_argc(op, code)
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
            self.fromname = self.co.co_names[argc]
        elif IMPORT_STAR == op:
            assert self.import_name

            # from ... import * is currently not fully supported
            #self.has_star = True
            self.fromname = '*'
            self.store_name('*')

        elif STORE_NAME == op:
            self.store_name(self.co.co_names[argc])
        elif POP_TOP == op:
            self.clear_states()

    def clear_states(self):
        self.import_name = self.fromname = None
        self.fqn = self.store = None
        del self.consts[:]

    def store_name(self, name):
        if not self.import_name:
            return

        assert len(self.consts) >= 2
        level = self.consts[-2]
        assert level >= -1

        if not self.fromname:
            # import ...
            symbol = self.fqn[self.store:]
            symbol.insert(0, name)
            self.imports.append(('.'.join(symbol), '.'.join(self.fqn), level))
            self.clear_states()
        else:
            # from ... import ...
            fqn = '.'.join(self.fqn + [self.fromname])
            self.imports.append((name, fqn, level))
            self.fromname = None


if __name__ == "__main__":
    import doctest
    doctest.testmod()
