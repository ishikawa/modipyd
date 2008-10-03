#
# Common tasks for project
#

.PHONY: all test lint doc web clean

all: lint test

test: test24
	PYTHONPATH=. python tests/runtests.py

test24:
	if [ -f "$(PYTHON24)" -a -x "$(PYTHON24)" ]; then \
		$(MAKE) clean; \
		PYTHONPATH=. "$(PYTHON24)" tests/runtests.py; \
		$(MAKE) clean; \
	fi

lint:
	pylint --rcfile .pylintrc --disable-msg-cat=R --disable-msg=I0011,C0103,C0111,W0142 modipyd
	pylint --rcfile .pylintrc --disable-msg-cat=R --disable-msg=I0011,C0103,C0111,C0103,R0904,W0142,C0102 tests

# Generate offline documentation
doc:
	cd docs; $(MAKE)

# Generate online documentation
webdoc:
	cd docs; $(MAKE) online

clean:
	-find . -name \*.py[co] -exec rm -f {} \;
