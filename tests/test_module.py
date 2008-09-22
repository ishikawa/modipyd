#!/usr/bin/env python

import unittest
import modipyd.module
from tests import TestCase, FILES_DIR


class TestModipydModule(TestCase):

    def test_init(self):
        module = modipyd.module.Module('', '')
        self.assertNotNone(module)


if __name__ == '__main__':
    unittest.main()
