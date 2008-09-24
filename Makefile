#
# Common tasks for project
#

.PHONY: test lint

all: lint test

test:
	PYTHONPATH=. python tests/runtests.py

lint:
	pylint --rcfile .pylintrc --disable-msg-cat=R --disable-msg=I0011,C0103,C0111,W0142 modipyd
	pylint --rcfile .pylintrc --disable-msg-cat=R --disable-msg=I0011,C0103,C0111,C0103,R0904,W0142 tests/*.py