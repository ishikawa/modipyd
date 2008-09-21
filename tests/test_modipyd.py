#!/usr/bin/env python

import unittest
import modipyd
import tests


class TestModipyd(tests.TestCase):
    """Tests modipyd module"""

    def test_logger(self):
        self.assertNotNone(modipyd.LOGGER)


if __name__ == '__main__':
    unittest.main()
