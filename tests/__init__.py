"""
Regression tests for modipyd

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

import sys
import unittest
from os.path import join, dirname

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
