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
        print filename
        if filename.endswith('.py'):
            try:
                mtime = os.path.getmtime(filename)
            except os.error:
                LOGGER.warn(
                    "The file at %s does not exist"
                    " or is inaccessible, ignore." % filename)
            else:
                print "Monitoring:\t", filename
                scripts.append(filename)
                mtimes[filename] = mtime

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
            #os.system("python ./tests/runtests.py")
    except KeyboardInterrupt:
        LOGGER.debug('KeyboardInterrupt', exc_info=True)

def run():
    main(sys.argv[1:] or os.getcwd())


if __name__ == '__main__':
    run()
