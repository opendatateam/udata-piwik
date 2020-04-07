#!/usr/bin/env python
import io
import os
import re

from setuptools import setup

RE_BADGE = re.compile(r'^\[\!\[(?P<text>.*?)\]\[(?P<badge>.*?)\]\]\[(?P<target>.*?)\]$', re.M)

BADGES_TO_KEEP = ['gitter-badge']


def md(filename):
    '''
    Load .md (markdown) file and sanitize it for PyPI.
    '''
    content = io.open(filename).read()

    for match in RE_BADGE.finditer(content):
        if match.group('badge') not in BADGES_TO_KEEP:
            content = content.replace(match.group(0), '')

    return content


def pip(filename):
    """Parse pip reqs file and transform it to setuptools requirements."""
    return open(os.path.join('requirements', filename)).readlines()


long_description = '\n'.join((
    md('README.md'),
    md('CHANGELOG.md'),
    ''
))

install_requires = pip('install.pip')
tests_require = pip('test.pip')


setup(
    name='udata-piwik',
    version='2.0.1',
    description='Piwik support for uData',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/opendatateam/udata-piwik',
    author='OpenDataTeam',
    author_email='contact@opendata.team',
    packages=['udata_piwik'],
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    entry_points={
        'udata.commands': [
            'piwik = udata_piwik.commands:piwik',
        ],
        'udata.models': [
            'piwik = udata_piwik.models',
        ],
        'udata.tasks': [
            'piwik = udata_piwik.tasks',
        ],
        'udata.views': [
            'piwik = udata_piwik.views',
        ],
    },
    license='LGPL',
    zip_safe=False,
    keywords='udata piwik',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
