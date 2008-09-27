#!/usr/bin/env python

import unittest

from modipyd.descriptor import OrderedSet
from tests import TestCase


class TestOrderedSet(TestCase):

    def test_init(self):
        objects = OrderedSet()
        self.assertNotNone(objects)

    def test_empty(self):
        objects = OrderedSet()
        self.assertEqual(0, len(objects))
        self.assert_(123 not in objects)
        self.assertRaises(IndexError, objects.__getitem__, 0)

    def test_some_elements(self):
        objects = OrderedSet()
        self.assertEqual(0, len(objects))

        objects.add(1)
        objects.add("Hello")
        objects.add((1, 2, 3))

        self.assertEqual(3, len(objects))
        self.assert_(1 in objects)
        self.assert_("Hello" in objects)
        self.assert_((1, 2, 3) in objects)
        self.assert_(2 not in objects)
        self.assert_("HELLO" not in objects)

        self.assertEqual(1, objects[0])
        self.assertEqual("Hello", objects[1])
        self.assertEqual((1, 2, 3), objects[2])

    def test_update(self):
        objects = OrderedSet([1, 2, 3])
        self.assertEqual(3, len(objects))

        objects.update([4, 5, 6])
        self.assertEqual(6, len(objects))

        objects.update([1, 2, 3])
        self.assertEqual(6, len(objects))

        objects.update([1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(7, len(objects))

        for i in xrange(7):
            self.assertEqual(i+1, objects[i])

    def test_iter(self):
        objects = OrderedSet()
        for i in xrange(10):
            objects.add(i)

        it = iter(objects)
        for i in xrange(10):
            self.assertEqual(i, it.next())
        self.assertRaises(StopIteration, it.next)

    def test_clear(self):
        objects = OrderedSet()
        self.assertEqual(0, len(objects))
        objects.clear()
        self.assertEqual(0, len(objects))

        objects.update([1, 2, 3])
        self.assertEqual(3, len(objects))
        objects.clear()
        self.assertEqual(0, len(objects))

    def test_remove(self):
        objects = OrderedSet([1, 2, 3])
        self.assertEqual(3, len(objects))

        objects.remove(2)
        self.assertEqual(2, len(objects))
        self.assertEqual(1, objects[0])
        self.assertEqual(3, objects[1])

        objects.remove(3)
        self.assertEqual(1, len(objects))
        self.assertEqual(1, objects[0])

        objects.add(1)
        self.assertEqual(1, len(objects))
        self.assertEqual(1, objects[0])

        objects.remove(1)
        self.assertEqual(0, len(objects))


if __name__ == '__main__':
    unittest.main()
