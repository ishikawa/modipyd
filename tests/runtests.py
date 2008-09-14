#! /usr/bin/env python

"""
Regression tests for modipyd
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import modipyd

# ----------------------------------------------------------------
# Settings
# ----------------------------------------------------------------
# The directory contains test files.
FILES_DIR = os.path.join(os.path.dirname(__file__))


class TestModipyd(unittest.TestCase):
    """Tests modipyd functionalities"""

    def test_files_dir_exists(self):
        self.assert_(os.path.exists(FILES_DIR))



if __name__ == '__main__':
    unittest.main()
