"""
The core functions module of ``modipyd.utils`` package.

.. note::
   These functions are separated from ``modipyd.utils.__init__.py``
   so that the package is prevented from cyclic import problem.

"""

__all__ = ['sequence']


def sequence(obj, copy=None):
    """
    Returns a sequence (usually tuple) whose element is ``obj``.
    If a callable argument ``copy`` is specified, it is called
    with the sequence as 1st argument, and returns its result.

    >>> sequence(None)[0] is None
    True
    >>> sequence("")
    ('',)
    >>> sequence([])
    []
    >>> sequence(())
    ()
    >>> sequence(123, copy=tuple)
    (123,)
    >>> sequence(123, copy=list)
    [123]
    """
    if isinstance(obj, (list, tuple)):
        seq = obj
    else:
        seq = (obj,)

    if copy is not tuple and callable(copy):
        seq = copy(seq)

    return seq


if __name__ == "__main__":
    import doctest
    doctest.testmod()
