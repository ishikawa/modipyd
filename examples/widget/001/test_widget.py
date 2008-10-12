import unittest
from widget import Widget

class SimpleWidgetTestCase(unittest.TestCase):

    def test_init(self):
        widget = Widget('The widget', 10, 10)
        self.failUnless(widget.size() == (10, 10),
                        'incorrect size')

    def test_default_size(self):
        widget = Widget('The widget')
        self.failUnless(widget.size() == (50, 50),
                        'incorrect default size')

if __name__ == '__main__':
    unittest.main()
