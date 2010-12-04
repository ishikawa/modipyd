#
# Common tasks for project
#

.PHONY: all test test2x lint doc web clean distclean realclean

PYLINT_DISABLE_MSG = I0011,C0103,C0111,C0322,W0142

all: lint test

test:
	python tests/runtests.py

test2x:
	for version in $(PYTHON24) $(PYTHON25) $(PYTHON26) $(PYTHON27); do \
		if [ -f "$${version}" -a -x "$${version}" ]; then \
			$(MAKE) clean; \
			"$${version}" tests/runtests.py; \
		fi \
	done; \
	$(MAKE) clean;

lint:
	pylint --rcfile .pylintrc --disable-msg-cat=R --disable-msg=$(PYLINT_DISABLE_MSG) modipyd

doc:
	cd docs; $(MAKE)

clean:
	-find . -name \*.py[co] -exec rm -f {} \;
	python setup.py clean

distclean: clean
	rm -rf build/*
	rm -rf dist/*

realclean: distclean
	cd docs; $(MAKE) clean
