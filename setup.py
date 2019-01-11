#!/usr/bin/env python
from setuptools import setup
import os

base = os.path.dirname(os.path.abspath(__file__))

VERSION = open(os.path.join(base, 'version.txt')).read()[:-1]

pkg_dir = os.path.join(base, 'lpi')
pkg_name = 'lpi'

requires = ['pplpy>=0.7.1', 'z3-solver']

dependency_links = [
    'git+https://github.com/jesusjda/pplpy.git#egg=pplpy-0.7.1'
]
solver_name = "solvers"
lp_name = "lp"
solver_dir = os.path.join(pkg_dir, solver_name)
lp_dir = os.path.join(pkg_dir, lp_name)
solver_name = pkg_name + "." + solver_name
lp_name = pkg_name + "." + lp_name

setup(
    name='pylpi',
    version=VERSION,
    description='Linnear Programming Common Interface for ppl and z3',
    long_description=open(os.path.join(base, "README.md")).read(),
    author='Jesus Domenech',
    author_email='jdomenec@ucm.es',
    url='https://github.com/jesusjda/pyLPi',
    download_url='https://github.com/jesusjda/pyLPi/archive/{}.tar.gz'.format(VERSION),
    license='GPL v3',
    platforms=['any'],
    packages=[pkg_name, solver_name, lp_name],
    package_dir={pkg_name: pkg_dir, solver_name: solver_dir, lp_name: lp_dir},
    package_data={pkg_name: ['*.py'], solver_name: ['*.py'], lp_name: ['*.py']},
    install_requires=requires,
    dependency_links=dependency_links,
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
    keywords=['linear-programming', 'ppl', 'z3', 'polyhedra']
)
