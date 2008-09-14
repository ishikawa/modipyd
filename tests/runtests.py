#! /usr/bin/env python

"""
Regression tests for modipyd
"""

import os
import sys
import unittest
from errno import ENOENT

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import modipyd

# ----------------------------------------------------------------
# Settings
# ----------------------------------------------------------------
# The directory contains test files.
FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')


class TestModipydCollectFiles(unittest.TestCase):
    """Tests modipyd functionalities"""

    def test_files_dir_exists(self):
        self.assert_(os.path.exists(FILES_DIR))
        self.assert_(os.path.isdir(FILES_DIR))

    def test_not_found(self):
        filename = os.path.join(FILES_DIR, 'no file or directory')
        self.assert_(not os.path.exists(filename))

        try:
            modipyd.collect_files(filename)
        except IOError, ioe:
            self.assert_(ioe.errno is ENOENT)
            self.assertEqual(filename, ioe.filename)
        else:
            self.fail("Expected IOError")

    def empty_directory(self):
        directory = os.path.join(FILES_DIR, 'empty')
        if not os.path.exists(directory):
            os.mkdir(directory)
        self.assert_(os.path.exists(directory))
        self.assert_(os.path.isdir(directory))
        return directory

    def test_empty_directory(self):
        directory = self.empty_directory()
        files = list(modipyd.collect_files(directory))
        self.assert_(files is not None)
        self.assertEqual(0, len(files))


if __name__ == '__main__':
    unittest.main()
