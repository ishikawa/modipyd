#!/usr/bin/env python

import os
import unittest
import unittest_helper
from modipyd.pyscript import PyScript


class TestPyScript(unittest_helper.TestCase):

    def test_init(self):
        print __file__
        filepath = os.path.abspath(__file__)
        script = PyScript(filepath)
        self.assertNotNone(script)
        self.assertEqual(filepath, script.filename)


if __name__ == '__main__':
    unittest.main()
