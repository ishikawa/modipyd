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
import os
import sys
import time
import modipyd
from modipyd import LOGGER


def monitor(filepath):
    mtimes = {}
    scripts = []
    for filename in modipyd.collect_files(filepath):
        if filename.endswith('.py'):
            print "Monitoring:\t", filename
            scripts.append(filename)
            mtimes[filename] = os.path.getmtime(filename)

    # uniqfy
    scripts = list(set(scripts))
    while scripts:
        time.sleep(1)
        for filename in scripts:
            if not os.path.exists(filename):
                # remove entry
                del scripts[filename]
                del mtimes[filename]
            else:
                mtime = os.path.getmtime(filename)
                try:
                    if mtime > mtimes[filename]:
                        yield filename
                finally:
                    mtimes[filename] = mtime


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def main(filepath):
    try:
        for modified in monitor(filepath):
            print "Modified:\t", modified
    except KeyboardInterrupt:
        LOGGER.debug('KeyboardInterrupt', exc_info=True)

def run():
    main(sys.argv[1:] or os.getcwd())


if __name__ == '__main__':
    run()
