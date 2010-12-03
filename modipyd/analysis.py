"""
Module Dependency Analysis

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""

import types

from modipyd import LOGGER, utils
from modipyd.utils import split_module_name
from modipyd.resolve import resolve_relative_modulename


def has_subclass(module_descriptor, baseclass):
    """
    Return ``True`` if the module has a class
    derived from *baseclass*
    """
    # We can't use ``unittest.TestLoader`` to loading tests,
    # bacause ``TestLoader`` imports (execute) module code.
    # If imported/executed module have a statement such as
    # ``sys.exit()``, ...program exit!

    if not isinstance(baseclass, (type, types.ClassType)):
        raise TypeError(
            "The baseclass argument must be instance of type or class, "
            "but was instance of %s" % type(baseclass))

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
    # 5. Check loaded class is *baseclass* or its subclass

    # Construct imported symbols.
    # This is used in phase 3.
    symbols = dict([(imp[0], imp) for imp in modcode.context['imports']])

    # 1. For all class definition in module code
    for klass in modcode.context['classdefs']:

        # 2. Check class is derived from base class(s)
        bases = klass[1]
        if not bases:
            continue

        # 3. Check base class(s) is imported from another module
        for base in bases:
            # Search imported symbol that is class name or module name
            if '.' in base:
                names = list(split_module_name(base))
            else:
                names = [base]

            import_ = symbols.get(names[0])
            if import_ is None:
                # Not an imported base class
                continue

            # Convert a name to a qualified module name
            #
            #   1. Resolve import alias if exists
            #   2. Qualify name as full module name
            #   3. Resolve relative module name
            #
            level = import_[2]
            names[0] = import_[1]

            fqn = '.'.join(names)
            fqn = resolve_relative_modulename(fqn, modcode.package_name, level)

            assert '.' in fqn, "fqn must be a qualified module fqn"
            LOGGER.debug("'%s' is derived from '%s'" % (module_descriptor.name, fqn))

            try:
                try:
                    klass = utils.import_component(fqn)
                except ImportError:
                    if level == -1 and modcode.package_name:
                        # The qualified name may be relative to current package.
                        fqn = '.'.join((modcode.package_name, fqn))
                        klass = utils.import_component(fqn)
                    else:
                        raise
            except (ImportError, AttributeError):
                LOGGER.warn("Exception occurred "
                    "while importing component '%s'" % fqn,
                    exc_info=True)
            else:
                # 5. Check loaded class is specified class or its subclass
                if isinstance(klass, (type, types.ClassType)) and \
                        issubclass(klass, baseclass):
                    return True

    return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
