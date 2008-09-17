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


class PythonScript(object):
    """Python source code file"""

    def __init__(self, filename):
        self.filename = filename
        self.mtime = os.path.getmtime(filename)

    def update(self):
        """Return True if updated"""
        try:
            mtime = os.path.getmtime(self.filename)
            return mtime > self.mtime
        finally:
            self.mtime = mtime

    def __hash__(self):
        return hash(self.filename)

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
            self.filename == other.filename)


def monitor(filepath):
    scripts = []
    for filename in modipyd.collect_files(filepath):
        if filename.endswith('.py'):
            try:
                modfile = PythonScript(filename)
                LOGGER.info("Monitoring %s" % filename)
            except os.error:
                LOGGER.warn(
                    "The file at %s does not exist"
                    " or is inaccessible, ignore." % filename)
            else:
                scripts.append(modfile)

    # uniqfy
    scripts = list(set(scripts))
    while scripts:
        time.sleep(1)
        # For in-place deletion (avoids copying the list),
        # Don't delete anything earlier in the list than
        # the current element through.
        for i, script in enumerate(reversed(scripts)):
            if not os.path.exists(script.filename):
                del script[-i]
            elif script.update():
                yield script.filename


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def main(filepath):
    try:
        for modified in monitor(filepath):
            LOGGER.info("Modified %s" % modified)
            #os.system("python ./tests/runtests.py")
    except KeyboardInterrupt:
        LOGGER.debug('KeyboardInterrupt', exc_info=True)

def run():
    main(sys.argv[1:] or os.getcwd())


if __name__ == '__main__':
    run()
