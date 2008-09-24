import sys
from os.path import join, dirname
import unittest
import os as altos


class A:
    """old-style"""
    pass

class B(object):
    """new-style"""
    pass

class C(unittest.TestCase):
    pass

class D(A, C):
    pass
