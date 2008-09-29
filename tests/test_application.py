#!/usr/bin/env python

import unittest
from tests import TestCase
from modipyd.application import Application


# pylint: disable-msg=W0613
class TestApplication(TestCase):

    def test_init(self):
        application = Application()
        self.assertNotNone(application)
        self.assertNotNone(application.paths)

    def test_update_variables(self):
        application = Application()
        self.assertEqual(0, len(application.variables))
        self.assertRaises(TypeError, application.update_variables, None)

        application.update_variables({})
        self.assertEqual(0, len(application.variables))

        application.update_variables({'var1':1, 'var2':2})
        self.assertEqual(2, len(application.variables))
        self.assertEqual(1, application.variables['var1'])
        self.assertEqual(2, application.variables['var2'])

    def test_plugins(self):
        application = Application()
        self.assertEqual(0, len(application.plugins))

        invoked = [False, False]

        def simple_plugin(event, monitor, context):
            invoked[0] = True

        class SimplePlugin(object):

            def __init__(self, event, monitor, context):
                self.event = event

            def __call__(self):
                invoked[1] = True

        application.install_plugin(simple_plugin)
        self.assertEqual(1, len(application.plugins))
        self.assertEqual(simple_plugin, application.plugins[0])
        application.install_plugin(SimplePlugin)
        self.assertEqual(2, len(application.plugins))
        self.assertEqual(SimplePlugin, application.plugins[1])

        self.assert_(not invoked[0])
        self.assert_(not invoked[1])
        # passing dummy objects
        application.invoke_plugins(object(), object())
        self.assert_(invoked[0])
        self.assert_(invoked[1])

    def test_plugin_context(self):
        application = Application()
        application.update_variables(dict(var1=123, var2='HELLO'))

        invoked_context = {}

        def context_plugin(event, monitor, context):
            invoked_context.update(context)

        application.install_plugin(context_plugin)
        self.assertEqual(0, len(invoked_context))
        # passing dummy objects
        application.invoke_plugins(object(), object())
        self.assertEqual(2, len(invoked_context))
        self.assertEqual(123, invoked_context['var1'])
        self.assertEqual('HELLO', invoked_context['var2'])


if __name__ == '__main__':
    unittest.main()
