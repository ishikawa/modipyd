"""
Functions that help with dynamically creating decorators.

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""

from types import NoneType
from modipyd.utils.core import wrap_sequence


def require(**types):
    """
    Lets you annotate function with argument type requirements.
    These type requirements are automatically checked by the system at
    function invocation time.
    """

    # pylint: disable-msg=W0622
    def decorator(fn):
        code = fn.func_code
        argnames = code.co_varnames[:code.co_argcount]
        argmaps = dict((name, i) for i, name in enumerate(argnames))

        # None -> NoneType convertion
        for name, constraints in types.iteritems():
            constraints = wrap_sequence(constraints)
            constraints = [c is None and NoneType or c for c in constraints]
            if len(constraints) == 1:
                types[name] = constraints[0]
            else:
                types[name] = tuple(constraints)

        # pylint: disable-msg=W0621
        # :W0621: *Redefining name %r from outer scope (line %s)*
        def type_checker(*args, **kwargs):
            for name in argmaps:
                i = argmaps[name]
                if i < len(args):
                    value = args[i]
                elif name in kwargs:
                    value = kwargs[name]
                else:
                    # maybe default value
                    continue

                try:
                    constraint = types[name]
                    if (callable(constraint) and
                            not isinstance(constraint, type)):
                        if not constraint(value): 
                            raise TypeError("Type checking of '%s' was failed: "
                                "%s(%s)" % (name, value, type(value)))
                    elif not isinstance(value, constraint):
                        raise TypeError(
                                "Expected '%s' to be %s, but was %s." %
                                (name, types[name], type(value)))
                except KeyError:
                    pass

            return fn(*args, **kwargs)

        type_checker.__name__ = fn.__name__
        type_checker.__module__ = fn.__module__
        type_checker.__dict__ = fn.__dict__
        type_checker.__doc__ = fn.__doc__
        return type_checker

    return decorator
