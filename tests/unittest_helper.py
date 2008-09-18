import os
import sys
import unittest

from os.path import join, normpath, dirname
sys.path.insert(0, join(dirname(__file__), '..'))


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
