#
# Common tasks for project
#

.PHONY: test lint

test:
	python test/runtests.py

lint:
	pylint --rcfile .pylintrc modipyd