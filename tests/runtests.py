#! /usr/bin/env python

"""
Regression tests for modipyd
"""

import os
import sys
import unittest
from errno import ENOENT
from os.path import join, normpath, dirname

sys.path.insert(0, join(dirname(__file__), '..'))
import modipyd

# ----------------------------------------------------------------
# Settings
# ----------------------------------------------------------------
# The directory contains test files.
FILES_DIR = join(dirname(__file__), 'files')

class TestCase(unittest.TestCase):
    """Custom TestCase class"""

    def failUnlessNone(self, expr, msg=None):
        """Fail the test unless the expression is None."""
        if expr is not None:
            raise self.failureException, msg

    def failIfNone(self, expr, msg=None):
        """Fail the test if the expression is None."""
        if expr is None:
            raise self.failureException, msg

    # Synonyms for assertion methods
    assertNone = failUnlessNone
    assertNotNone = failIfNone


class TestModipydCollectFiles(TestCase):
    """Tests modipyd functionalities"""

    def test_files_dir_exists(self):
        self.assert_(os.path.exists(FILES_DIR))
        self.assert_(os.path.isdir(FILES_DIR))

    def test_not_found(self):
        filename = join(FILES_DIR, 'no file or directory')
        self.assert_(not os.path.exists(filename))

        try:
            list(modipyd.collect_files(filename))
        except IOError, ioe:
            self.assertEqual(ENOENT, ioe.errno)
            self.assertEqual(filename, ioe.filename)
        else:
            self.fail("Expected IOError")

    def empty_directory(self):
        directory = join(FILES_DIR, 'empty')
        if not os.path.exists(directory):
            os.mkdir(directory)
        self.assert_(os.path.exists(directory))
        self.assert_(os.path.isdir(directory))
        return directory

    def test_empty_directory(self):
        directory = self.empty_directory()
        files = list(modipyd.collect_files(directory))
        self.assertNotNone(files)
        self.assertEqual(0, len(files))

    def test_files(self):
        directory = join(FILES_DIR, '000')
        files = list(modipyd.collect_files(directory))
        self.assertNotNone(files)
        self.assertEqual(6, len(files))

        files[:] = [normpath(f) for f in files]
        self.assert_(directory not in files)
        for f in ['001', '002', '003', '004/A', '004/B', '004/C']:
            f = normpath(join(directory, f))
            self.assert_(f in files)


if __name__ == '__main__':
    unittest.main()
