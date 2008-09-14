#! /usr/bin/env python

"""
Regression tests for modipyd
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import modipyd


class TestModipydFunctions(unittest.TestCase):
    """Tests modipyd functions"""

    pass

if __name__ == '__main__':
    unittest.main()
