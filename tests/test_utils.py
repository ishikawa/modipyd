#! /usr/bin/env python

import unittest_helper
import modipyd
from modipyd import utils


class TestModipyd(unittest_helper.TestCase):
    """Tests modipyd module"""

    def test_logger(self):
        self.assertNotNone(modipyd.LOGGER)

    def test_wrap_sequence(self):
        self.assertEqual([], utils.wrap_sequence([]))
        self.assertEqual([1, 2, 3], utils.wrap_sequence([1, 2, 3]))
        self.assertEqual((1,), utils.wrap_sequence(1))
        self.assertEqual([1], utils.wrap_sequence(1, list))


if __name__ == '__main__':
    unittest.main()
