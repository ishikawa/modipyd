#
# Common tasks for project
#

.PHONY: test lint

all: lint test

test:
	python tests/runtests.py

lint:
	pylint --rcfile .pylintrc --disable-msg=C0111 modipyd
	pylint --rcfile .pylintrc --disable-msg=C0111,C0103,R0904 tests/runtests.py