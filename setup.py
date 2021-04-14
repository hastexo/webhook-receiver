#!/usr/bin/env python
"""Setup for the webhook receiver app."""

import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='webhook-receiver',
    use_scm_version=True,
    description='edX Webhooks: a webhook processor interfacing with Open edX',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hastexo/webhook-receiver',
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
        'django>=2.2',
        'django-celery>=3.2.1',
        'django_fsm',
        'edx-rest-api-client>=1.9.2',
        'edx-auth-backends>=2.0.2',
        'django-jsonfield-backport'
    ],
    setup_requires=[
        'setuptools-scm<6',
    ],
    entry_points={
        'lms.djangoapp': [
            'webhook_receiver = webhook_receiver.apps:WebhookReceiverConfig',
            'webhook_receiver_shopify = webhook_receiver_shopify.apps:WebhookReceiverShopifyConfig',  # NOQA
            'webhook_receiver_woocommerce = webhook_receiver_woocommerce.apps:WebhookReceiverWoocommerceConfig',  # NOQA
        ]
    }
)
