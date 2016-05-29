#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#
# A setuptools-based setup module for the project.
#

import ast
import os
import re
from setuptools import setup


# Utility function to read the contents of the given file.
def read_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        return f.read()


def get_project_version():
    # Based on:
    #
    #   https://packaging.python.org/en/latest/single_source_version.html
    #   https://github.com/mitsuhiko/flask/blob/master/setup.py
    #
    return ast.literal_eval(
        re.search(
            r'__version__\s+=\s+(.*)',
            read_file(os.path.join('retdec', '__init__.py'))
        ).group(1)
    )


setup(
    name='retdec-python',
    version=get_project_version(),
    description=(
        'A Python library and tools providing easy access to the retdec.com '
        'decompilation service through their public REST API.'
    ),
    long_description=read_file('README.rst'),
    author='Petr Zemek',
    author_email='s3rvac@gmail.com',
    url='https://github.com/s3rvac/retdec-python',
    license=read_file('LICENSE'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='retdec decompiler decompilation analysis fileinfo',
    packages=['retdec', 'retdec.tools'],
    install_requires=['requests'],
    scripts=[
        os.path.join('scripts', 'decompiler'),
        os.path.join('scripts', 'fileinfo')
    ]
)
