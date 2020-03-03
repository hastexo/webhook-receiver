# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

from django.conf import settings

from django.test import TestCase

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class ShopifyTestCase(TestCase):

    def setup_payload(self):
        # Grab an example payload and make it available to test
        # methods as a raw string and as a JSON dictionary.
        payload_file = os.path.join(os.path.dirname(__file__),
                                    'post.json')
        self.raw_payload = open(payload_file, 'rb').read()
        self.json_payload = json.load(open(payload_file, 'r'))

    def setup_course(self):
        # TODO: Set up a mock course
        course_id_string = 'course-v1:org+course+run1'
        course = Mock()
        course.id = course_id_string

    def setup_requests(self):
        self.token_uri = '%s/oauth2/access_token' % settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT  # noqa: E501
        self.enroll_uri = '%s/api/bulk_enroll/v1/bulk_enroll/' % settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT  # noqa: E501

        self.token_response = {
            'access_token': 'foobar',
            'expires_in': 3600
        }
