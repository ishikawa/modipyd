#
# Common tasks for project
#

.PHONY: all test lint doc web clean distclean realclean

PYLINT_DISABLE_MSG = I0011,C0103,C0111,C0322,W0142

all: lint test

test: test24
	python tests/runtests.py

test24:
	if [ -f "$(PYTHON24)" -a -x "$(PYTHON24)" ]; then \
		$(MAKE) clean; \
		"$(PYTHON24)" tests/runtests.py; \
		$(MAKE) clean; \
	fi

lint:
	pylint --rcfile .pylintrc --disable-msg-cat=R --disable-msg=$(PYLINT_DISABLE_MSG) modipyd

# Generate offline documentation
doc:
	cd docs; $(MAKE)

# Generate online documentation
webdoc:
	cd docs; $(MAKE) online

clean:
	-find . -name \*.py[co] -exec rm -f {} \;
	python setup.py clean

distclean: clean
	rm -rf build/*
	rm -rf dist/*

realclean: distclean
	cd docs; $(MAKE) clean
