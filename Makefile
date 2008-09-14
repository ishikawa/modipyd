#
# Common tasks for project
#

.PHONY: test lint

test:
	python tests/runtests.py

lint:
	pylint --rcfile .pylintrc modipyd tests/runtests.py