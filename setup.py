#!/usr/bin/env python

from setuptools import setup

import pychatbot


def read(filename):
    with open(filename) as file:
        return file.read().split('\n')


def get_requirements(req):
    if req.startswith('-r'):
        for line in read(req.split()[1]):
            for subreq in get_requirements(line):
                yield subreq
    elif req:
        yield req


setup(
    name='pychatbot',
    version=pychatbot.__version__,
    author=pychatbot.__author__,
    author_email=pychatbot.__email__,
    description='A lib to create chatbots',
    url='http://github.com/greenkey/pychatbot/',
    packages=['pychatbot', 'pychatbot.endpoints'],
    include_package_data=True,
    platforms='any',
    keywords=['chat', 'chatbot', 'telegram', 'twitter'],
    tests_require=list(get_requirements('-r requirements-dev.txt')),
    install_requires=list(get_requirements('-r requirements.txt')),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
