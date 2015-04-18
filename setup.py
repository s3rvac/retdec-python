#!/usr/bin/env python3
#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#
# A setuptools-based setup module for the project.
#

from setuptools import setup

# Utility function to read the contents of the given file.
def read_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        return f.read()

setup(
    name='retdec-python',
    version='0.0',
    description=(
        'A Python library and tools providing easy access to the retdec.com '
        'decompilation service through their public REST API.'
    ),
    long_description=read_file('README.md'),
    author='Petr Zemek',
    author_email='s3rvac@gmail.com',
    url='https://github.com/s3rvac/retdec-python',
    license=read_file('LICENSE'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='retdec decompiler decompilation analysis fileinfo',
    packages=['retdec'],
    install_requires=['requests']
)
