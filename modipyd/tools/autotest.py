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
import logging
from optparse import OptionParser

import modipyd
from modipyd import LOGGER


# ----------------------------------------------------------------
# Version
# ----------------------------------------------------------------
MAJOR_VERSION = 0
MINOR_VERSION = 1
VERSION_STRING = "%d.%d" % (MAJOR_VERSION, MINOR_VERSION)


# ----------------------------------------------------------------
# API, Functions, Classes...
# ----------------------------------------------------------------
class PythonScript(object):
    """Python source code file"""

    def __init__(self, filename):
        self.filename = filename
        # Instance variable ``mtime`` will be updated by ``update()``
        self.mtime = None
        self.update()
        assert self.mtime is not None

    def update(self):
        """Return True if updated"""
        try:
            mtime = os.path.getmtime(self.filename)
            return self.mtime is None or mtime > self.mtime
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
def main(options, filepath):
    """
    Monitoring modules on the search path ``path``. If ``path`` is
    a list of directory names, each directory is searched for files
    with '.py' suffix. They are also inserted into ``sys.path`` so that
    program can import monitoring modules.
    """
    # options handling
    if options.verbose:
        LOGGER.setLevel(logging.INFO)
    if options.debug:
        LOGGER.setLevel(logging.DEBUG)

    # start monitoring
    try:
        # Make filepath iterable.
        filepath = modipyd.wrap_sequence(filepath)
        assert not isinstance(filepath, basestring)

        # Insert directories path into the head of ``sys.path``
        # so that ``monitor()`` can import found modules.
        # Notes: For the proper order of specified filepaths,
        # inserts path in reverse order.
        for f in reversed(filepath):
            if os.path.isdir(f):
                sys.path.insert(0, f)
                LOGGER.info("sys.path: %s" % f)

        for modified in monitor(filepath):
            LOGGER.info("Modified %s" % modified)
            #os.system("python ./tests/runtests.py")
    except KeyboardInterrupt:
        LOGGER.debug('KeyboardInterrupt', exc_info=True)

def run():
    """Standalone program interface"""
    parser = OptionParser(
        usage="usage: %prog [options] [files or directories]",
        version=("%prog " + VERSION_STRING))

    parser.add_option("-v", "--verbose",
        action="store_true", dest="verbose", default=False,
        help="Make the operation more talkative")
    parser.add_option("--debug",
        action="store_true", dest="debug", default=False,
        help="Make the operation more talkative (debug mode)")

    (options, args) = parser.parse_args()
    #main(options, args or os.getcwd())
    main(options, args or '.')


if __name__ == '__main__':
    run()
