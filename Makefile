#
# Common tasks for project
#

.PHONY: test lint

all: lint test

test:
	python tests/runtests.py

lint:
	pylint --rcfile .pylintrc modipyd tests/runtests.py