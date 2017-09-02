"""
 * Copyright (c) 2016. Mingyu Gao
 * All rights reserved.
 *
"""
import os
import re
import setuptools

PACKAGE = 'energydram'
DESC = 'DRAM energy calculation.'

def _get_version():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, PACKAGE, '__init__.py'), 'r') as fh:
        matches = re.findall(r'^\s*__version__\s*=\s*[\'"]([^\'"]+)[\'"]',
                             fh.read(), re.M)
        if matches:
            return matches[-1]
    return '0.0.0'

def _readme():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.rst'), 'r') as fh:
        return fh.read()

setuptools.setup(
    name=PACKAGE,
    version=_get_version(),
    description=DESC,

    author='Mingyu Gao',
    author_email='mgao12@stanford.edu',
    long_description=_readme(),
    url='https://github.com/gaomy3832/energydram',
    license='BSD 3-clause',

    packages=setuptools.find_packages(),

    install_requires=[
        'numpy>=1.8',
        'coverage>=4',
        'pytest>=3',
        'pytest-cov>=2',
        'pytest-xdist>=1',
    ],

    keywords='DRAM energy',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Hardware',
        'Topic :: Utilities',
    ],
)

