"""
The ``ordered_set`` module provides classes for constructing and
manipulating **ordered** collections of unique elements.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import weakref

__all__ = ['OrderedSet']


class _Node(object):

    def __init__(self, element):
        self.element = element
        self.next = None
        self.__prev = None

    def get_prev(self):
        return self.__prev() if self.__prev is not None else None

    def set_prev(self, node):
        self.__prev = weakref.ref(node) if node is not None else None

    prev = property(get_prev, set_prev)


class OrderedSet(object):
    """
    A linked-list with a uniqueness constraint and O(1) lookups/removal.
    """

    def __init__(self, iterable=()):
        self.__map = {}
        self.__start = self.__end = None
        self.extend(iterable)

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return repr(list(self))

    def __len__(self):
        return len(self.__map)

    def __contains__(self, element):
        return element in self.__map

    # O(n) performance
    def __getitem__(self, i):
        curnode = self.__start
        while curnode is not None:
            if i == 0:
                return curnode.element
            else:
                i -= 1
                curnode = curnode.next
        raise IndexError("list index out of range")

    def __iter__(self):
        curnode = self.__start
        while curnode is not None:
            yield curnode.element
            curnode = curnode.next

    def extend(self, iterable):
        """
        Extend the right side of the OrderedSet with
        elements from the iterable.
        """
        self.update(iterable)

    def append(self, element):
        self.add(element)

    def update(self, iterable):
        """Update set, adding elements from iterable"""
        for element in iterable:
            self.add(element)

    def add(self, element):
        """Add element to set"""
        if element in self.__map:
            return
        node = _Node(element)
        if self.__end is not None:
            node.prev = self.__end
            self.__end.next = node
        if self.__start is None:
            self.__start = node
        self.__end = node
        self.__map[element] = node

    def remove(self, element):
        node = self.__map.pop(element)
        prevnode, nextnode = node.prev, node.next
        if prevnode:
            prevnode.next = nextnode
        if nextnode:
            nextnode.prev = prevnode
        if node is self.__start:
            self.__start = nextnode
        if node is self.__end:
            self.__end = prevnode

    def clear(self):
        """remove all items"""
        self.__map.clear()
        self.__start = self.__end = None
