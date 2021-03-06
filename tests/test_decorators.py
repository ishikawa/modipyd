#!/usr/bin/env python

import unittest
from modipyd.utils.decorators import require
from tests import TestCase


# pylint: disable-msg=W0613
class RequireDecoratorTestCase(TestCase):

    def test_simple(self):

        @require(x=int)
        def foo(x):
            return x

        self.assertEqual(foo(1), 1)
        self.assertEqual(foo(x=1), 1)
        self.assertRaises(TypeError, foo, 1.)

    def test_None_type(self):

        @require(x=(int, None))
        def foo(x):
            return x

        self.assertEqual(foo(1), 1)
        self.assertEqual(foo(x=1), 1)
        self.assertEqual(foo(x=None), None)
        self.assertRaises(TypeError, foo, 1.)

    def test_keyword_arguments(self):

        @require(x=int, y=(basestring, int))
        def foo(x, y, z):
            return x

        self.assertEqual(foo(1, 'string', 12.5), 1)
        self.assertEqual(foo(1, 123, 12.5), 1)
        self.assertEqual(foo(1, y=123, z=12.5), 1)
        self.assertRaises(TypeError, foo, 1, 2.5, 123)

    def test_callable_constraint(self):

        @require(x=lambda x: x == 'check me')
        def foo(x):
            return x

        self.assertEqual(foo('check me'), 'check me')
        self.assertEqual(foo(x='check me'), 'check me')
        self.assertRaises(TypeError, foo, 'check you')

    def test_default_value(self):

        @require(x=int)
        def foo(x=999):
            return x

        self.assertEqual(foo(), 999)
        self.assertEqual(foo(123), 123)
        self.assertRaises(TypeError, foo, "123")

    def test_docstring(self):

        @require(x=int)
        def foo(x):
            """function foo()"""
            return x

        @require(x=int)
        def hoge(x):
            """function hoge()"""
            return x

        self.assertEqual("""function foo()""", foo.__doc__)
        self.assertEqual("""function hoge()""", hoge.__doc__)


if __name__ == '__main__':
    unittest.main()
