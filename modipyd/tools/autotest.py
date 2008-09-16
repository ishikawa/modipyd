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

def collect(filepath):
    if not os.path.isdir(filepath):
        yield filepath
    else:
        for dirpath, dirnames, filenames in os.walk(filepath):
            for filename in filenames:
                yield os.path.join(dirpath, filename)

def monitor(filepath):
    mtimes = {}
    scripts = []
    for filename in collect(filepath):
        if filename.endswith('.py'):
            print "Monitoring:\t", filename
            scripts.append(filename)
            mtimes[filename] = os.path.getmtime(filename)

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

def run():
    try:
        for filepath in sys.argv[1:]:
            #filepath = os.path.abspath(os.path.join(os.getcwd(), path))
            for modified in monitor(filepath):
                print "Modified:\t", modified
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run()
