#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-wetest',
    version='1.0.1',
    author='megachweng',
    author_email='megachweng@gmail.com',
    maintainer='megachweng',
    maintainer_email='megachweng@gmail.com',
    license='MIT',
    url='https://github.com/megachweng/pytest-wetest',
    description='Welian API Automation test framework pytest plugin',
    long_description=read('README.rst'),
    long_description_content_type="text/x-rst",
    py_modules=['pytest_wetest', 'utl'],
    python_requires='>=3.6',
    install_requires=['pytest>=3.8.0', 'requests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'wetest = pytest_wetest',
        ],
    },
)
