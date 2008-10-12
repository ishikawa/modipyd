"""
The core functions module of ``modipyd.utils`` package.
to prevent the package from cyclic import problem.
"""

__all__ = ['wrap_sequence', 'unwrap_sequence']


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

def unwrap_sequence(obj):
    """
    >>> unwrap_sequence([None]) is None
    True
    >>> unwrap_sequence([1])
    1
    >>> unwrap_sequence([1, 2, 3])
    [1, 2, 3]
    """
    if isinstance(obj, (list, tuple)) and len(obj) == 1:
        return obj[0]
    else:
        return obj


if __name__ == "__main__":
    import doctest
    doctest.testmod()
