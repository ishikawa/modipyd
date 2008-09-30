"""
autotest
================================================

quoted from http://www.zenspider.com/ZSS/Products/ZenTest/

> Improves feedback by running tests continuously.
> Continually runs tests based on files you've changed.
> Get feedback as soon as you save. Keeps you in your editor
> allowing you to get stuff done faster.
> Focuses on running previous failures until you've fixed them.

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""

from modipyd import LOGGER
from modipyd.tools import generic
from modipyd.application.plugins import Autotest


def make_application(options, args):
    # Create Application instance, and install Autotest plugin
    application = generic.make_application(options, args)
    application.install_plugin(Autotest)
    if options.runner:
        application.update_variables({
            Autotest.CONTEXT_TEST_RUNNER: options.runner,
        })
    return application

def make_option_parser():
    parser = generic.make_option_parser()
    parser.add_option("-r", "--runner", default=None,
        action="store", dest="runner", metavar='CLASS_NAME',
        help="qualified name of the unittest.TestRunner subclass "
             "(default: unittest.TextTestRunner)")
    return parser

def run():
    parser = make_option_parser()
    options, args = parser.parse_args()

    try:
        make_application(options, args or '.').run()
    except KeyboardInterrupt:
        LOGGER.debug('Keyboard Interrupt', exc_info=True)


if __name__ == '__main__':
    run()
