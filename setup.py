#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import modipyd

author, email = modipyd.__author__[:-1].split(' <')

setup(
    name = 'Modipyd',
    version = modipyd.__version__,
    url = modipyd.__url__,
    license = modipyd.__license__,
    author = author,
    author_email = email,
    description = '',
    long_description = modipyd.__doc__,
    keywords = 'test autotest bytecode dependency analysis',
    packages = find_packages(exclude=['tests']),
    entry_points = {
        'console_scripts': [
            'modipyd = modipyd.tools.generic:run',
            'autotest = modipyd.tools.autotest:run',
        ],
    },
    platforms = 'any',
    zip_safe = False,
    include_package_data = True,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: Japanese',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite = "tests.runtests.gather_tests",
)
