# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

__version__ = "0.1"

setup(
    name="melba",
    version=__version__,
    description="Build a Pelican blog from sources on github",
    author="gmflanagan",
    author_email = "gmflanagan@outlook.com",
    classifiers=["Development Status :: 4 - Beta",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: BSD License",
                "Programming Language :: Python",
                "Topic :: Software Development :: Libraries",
                "Topic :: Software Development :: Libraries :: Python Modules",
                ],
    url="https://github.com/averagehuman/python-melba",
    license="BSD",
    packages = find_packages(),
    scripts = [
        'bin/melba',
    ],
    include_package_data=True,
    zip_safe=False,
    tests_require=['pytest'],
)
    
