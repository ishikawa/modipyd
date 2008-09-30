"""
Functions that help with dynamically creating decorators.

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""

from types import NoneType
from modipyd.utils import wrap_sequence, unwrap_sequence


def require(**types):
    """
    Lets you annotate function with argument type requirements.
    These type requirements are automatically checked by the system at
    function invocation time.
    """

    def decorator(fn):
        code = fn.func_code
        argnames = code.co_varnames[:code.co_argcount]
        argmaps = dict((name, i) for i, name in enumerate(argnames))

        # None -> NoneType convertion
        for name, constraints in types.iteritems():
            constraints = wrap_sequence(constraints)
            constraints = [c is None and NoneType or c for c in constraints]
            types[name] = unwrap_sequence(tuple(constraints))

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

                constraint = types.get(name)
                if constraint is not None:
                    if (callable(constraint) and
                            not isinstance(constraint, type)):
                        check = constraint(value)
                        if not check in (True, False):
                            raise RuntimeError("Callable constraint must return"
                                " True or False, but was %s." % type(check))
                        if not constraint(value): 
                            raise TypeError("Type checking of '%s' was failed: "
                                "%s(%s)" % (name, value, type(value)))
                    elif not isinstance(value, constraint):
                        raise TypeError, "Expected '%s' to be %s,"\
                            " but was %s." % (name, types[name], type(value))

            return fn(*args, **kwargs)

        return type_checker
    return decorator
