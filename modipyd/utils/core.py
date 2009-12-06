"""
The core functions module of ``modipyd.utils`` package.

.. note::
   These functions are separated from ``modipyd.utils.__init__.py``
   so that the package is prevented from cyclic import problem.

"""

__all__ = ['wrap_sequence']


def wrap_sequence(obj, sequence_type=tuple):
    """
    Return a tuple whose item is obj.
    If obj is already a list or tuple, it is returned unchanged.

    >>> wrap_sequence(None)[0] is None
    True
    >>> wrap_sequence("")
    ('',)
    >>> wrap_sequence([])
    []
    >>> wrap_sequence(())
    ()
    >>> wrap_sequence(123, sequence_type=list)
    [123]
    """
    if isinstance(obj, (list, tuple)):
        return obj
    else:
        return sequence_type((obj,))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
