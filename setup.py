#!/usr/bin/env python
"""Setup for the edX Shopify app."""

import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='edx-webhooks',
    use_scm_version=True,
    version='0.0.1',
    description='edX Webhooks: a webhook processor interfacing with Open edX',
    url='https://github.com/hastexo/edx-webhooks',
    author='hastexo',
    author_email='pypi@hastexo.com',
    license='AGPL-3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Education :: Computer Aided Instruction (CAI)',
        'Topic :: Education',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'celery>=3.1.25',
        'django>=1.11.21',
        'django-celery>=3.2.1',
        'edx-rest-api-client>=1.9.2',
        'edx-auth-backends>=2.0.2',
    ],
    setup_requires=[
        'setuptools-scm',
    ],
)
