#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from setuptools import setup, find_packages

RE_MD_CODE_BLOCK = re.compile(r'```(?P<language>\w+)?\n(?P<lines>.*?)```', re.S)
RE_SELF_LINK = re.compile(r'\[(.*?)\]\[\]')
RE_LINK_TO_URL = re.compile(r'\[(?P<text>.*?)\]\((?P<url>.*?)\)')
RE_LINK_TO_REF = re.compile(r'\[(?P<text>.*?)\]\[(?P<ref>.*?)\]')
RE_LINK_REF = re.compile(r'^\[(?P<key>[^!].*?)\]:\s*(?P<url>.*)$', re.M)
RE_BADGE = re.compile(r'^\[\!\[(?P<text>.*?)\]\[(?P<badge>.*?)\]\]\[(?P<target>.*?)\]$', re.M)

BADGES_TO_KEEP = ['gitter-badge']

RST_BADGE = '''\
.. image:: {badge}
    :target: {target}
    :alt: {text}
'''

def md2pypi(filename):
    '''
    Load .md (markdown) file and sanitize it for PyPI.
    Remove unsupported github tags:
     - code-block directive
     - travis ci build badges
    '''
    content = open(filename).read()

    for match in RE_MD_CODE_BLOCK.finditer(content):
        rst_block = '\n'.join(
            ['.. code-block:: {language}'.format(**match.groupdict()), ''] +
            ['    {0}'.format(l) for l in match.group('lines').split('\n')] +
            ['']
        )
        content = content.replace(match.group(0), rst_block)

    refs = dict(RE_LINK_REF.findall(content))
    content = RE_LINK_REF.sub('.. _\g<key>: \g<url>', content)
    content = RE_SELF_LINK.sub('`\g<1>`_', content)
    content = RE_LINK_TO_URL.sub('`\g<text> <\g<url>>`_', content)

    for match in RE_BADGE.finditer(content):
        if match.group('badge') not in BADGES_TO_KEEP:
            content = content.replace(match.group(0), '')
        else:
            params = match.groupdict()
            params['badge'] = refs[match.group('badge')]
            params['target'] = refs[match.group('target')]
            content = content.replace(match.group(0),
                                      RST_BADGE.format(**params))
    # Must occur after badges
    for match in RE_LINK_TO_REF.finditer(content):
        content = content.replace(match.group(0), '`{text} <{url}>`_'.format(
            text=match.group('text'),
            url=refs[match.group('ref')]
        ))

    return content


long_description = '\n'.join((
    md2pypi('README.md'),
    md2pypi('CHANGELOG.md'),
    ''
))


install_requires = []
tests_require = []

setup(
    name='udata-piwik',
    version='0.9.0.dev',
    description='Piwik support for uData',
    long_description=long_description,
    url='https://github.com/opendatateam/udata-piwik',
    author='Opendata Team',
    author_email='opendatateam@data.gouv.fr',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    license='LGPL',
    use_2to3=True,
    keywords='udata piwik',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: System :: Software Distribution",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    ],
)
