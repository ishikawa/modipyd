import os
import sys

class Widget(object):
    """
    Widget is a User Interface (UI) component object. A widget
    object claims a rectagular region of its content, is responsible
    for all drawing within that region.
    """

    def __init__(self, name, width=50, height=50):
        self.name = name
        self.resize(width, height)

    def size(self):
        return (self.width, self.height)

    def resize(self, width, height):
        self.width, self.height = width, height