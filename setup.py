#!/usr/bin/env python
from setuptools import setup
import sys
import os

base = os.path.dirname(os.path.abspath(__file__))

VERSION = open(os.path.join(base, 'version.txt')).read()[:-1]

requires = []

if sys.version_info<(3,0,0):
    requires = ['pplpy', 'z3', 'cython', 'gmpy2', 'cysignals']
else:
    requires = ['pplpy', 'z3', 'gmpy2', 'cysignals']

dependencies = ["git+https://github.com/videlec/pplpy.git#egg=pplpy",
                "git+https://github.com/aleaxit/gmpy.git#egg=gmpy2"]

setup(
    name='pylpi',
    version=VERSION,
    description='Linnear Programming Common Interface for ppl and z3',
    long_description=open(os.path.join(base, "README.md")).read(),
    author='Jesus Domenech',
    author_email='jdomenec@ucm.es',
    url='https://github.com/jesusjda/pyLPi',
    download_url ='https://github.com/jesusjda/pyLPi/archive/{}.tar.gz'.format(VERSION),
    license='GPL v3',
    platforms=['any'],
    packages=['lpi'],
    package_dir={'lpi': os.path.join(base, 'lpi')},
    package_data={'lpi': ['*.py']},
    install_requires=requires,
    dependency_links=dependencies,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: C++",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Operating System :: Unix",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords=['linear-programming', 'ppl', 'z3', 'polyhedra'],
)
