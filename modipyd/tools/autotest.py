"""
autotest
================================================

quoted from http://www.zenspider.com/ZSS/Products/ZenTest/

> Improves feedback by running tests continuously.
> Continually runs tests based on files you've changed.
> Get feedback as soon as you save. Keeps you in your editor
> allowing you to get stuff done faster.
> Focuses on running previous failures until you've fixed them.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""

from modipyd import LOGGER
from modipyd.tools import generic
from modipyd.application.plugins import Autotest


def run():
    parser = generic.make_option_parser()
    (options, args) = parser.parse_args()

    # Create Application instance, and install Autotest plugin
    application = generic.make_application(options, args or '.')
    application.install_plugin(Autotest)

    try:
        application.run()
    except KeyboardInterrupt:
        LOGGER.debug('Keyboard Interrupt', exc_info=True)


if __name__ == '__main__':
    run()
