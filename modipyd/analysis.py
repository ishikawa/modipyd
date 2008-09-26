"""
Module Dependency Analysis

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

from modipyd import LOGGER, utils
from modipyd.utils import split_module_name


def testcase_module(module_descriptor):
    """
    Return ``True`` if the module in *module_descriptor*
    includes ``unittest.TestCase`` subclasses.
    """
    # We can't use ``unittest.TestLoader`` to loading tests,
    # bacause ``TestLoader`` imports (execute) module code.
    # If imported/executed module have a statement such as
    # ``sys.exit()``, ...program exit!

    modcode = module_descriptor.module_code
    assert modcode

    # How to check unittest.TestCase
    # ============================================
    # 1. For all class definition in module code
    # 2. Check class is derived from base class(s)
    # 3. Check base class(s) is imported from another module
    # 4. Load base class(s) from that module
    #    Notes: Assume the module contains base class does not have
    #           a dangerous code such as ``sys.exit``.
    # 5. Check loaded class is unittest.TestCase or its subclass

    # Construct imported symbols.
    # This is used in phase 3.
    symbols = dict([(imp[0], imp) for imp in modcode.imports])

    # 1. For all class definition in module code
    for klass in modcode.classdefs:

        # 2. Check class is derived from base class(s)
        bases = klass[1]
        if not bases:
            continue

        # 3. Check base class(s) is imported from another module
        for base in bases:
            # Search imported symbol that is class name or module name
            symbol = base
            if '.' in symbol:
                symbol = split_module_name(symbol)[0]

            import_ = symbols.get(symbol)
            if import_ is None:
                # Not an imported base class
                continue

            # Make name a qualified class name
            names = []
            parent = split_module_name(import_[1])[0]
            level = import_[2]
            if level > 0:
                # Relative imports
                packages = modcode.package_name.split('.')
                names.extend(packages[:len(packages) - (level-1)])
            if parent:
                names.extend(parent.split('.'))
            names.append(base)

            name = '.'.join(names)
            assert '.' in name, "names must be a qualified name"
            LOGGER.debug("'%s' is derived from "
                "imported class '%s'" % (base, name))

            try:
                baseclass = utils.import_component(name)
            except (ImportError, AttributeError):
                LOGGER.warn("Exception occurred "
                    "while importing component '%s'" % name,
                    exc_info=True)
            else:
                # 5. Check loaded class is unittest.TestCase or its subclass
                import types
                import unittest

                return (isinstance(baseclass, (type, types.ClassType)) and
                        issubclass(baseclass, unittest.TestCase))

    return False
