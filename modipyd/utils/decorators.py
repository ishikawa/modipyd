"""
Functions that help with dynamically creating decorators.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

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

        # None -> type(None) (= types.NoneType)
        for name in types:
            constraint = types[name]
            if type(constraint) in (tuple, list):
                constraint = tuple(type(None) if c is None else c for c in constraint)
            else:
                if constraint is None:
                    constraint = type(None)
            types[name] = constraint

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

                if name in types:
                    constraint = types[name]
                    if callable(constraint) and not isinstance(constraint, type):
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
