from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase

from webhook_receiver.utils import hmac_is_valid, lookup_course_id
from webhook_receiver.utils import SKULookupException

import requests_mock
from requests.exceptions import HTTPError


class SignatureVerificationTest(TestCase):

    def test_hmac_is_valid(self):
        correct_hmac = [
            ('hello',
             'world'.encode('utf-8'),
             '8ayXAutfryPKKRpNxG3t3u4qeMza8KQSvtdxTP/7HMQ='),
            ('bye',
             'bye'.encode('utf-8'),
             'HHfaL+C4HxPTexmlKO9pwEHuAXkErAz85APGPOgvBVU='),
            ('foo',
             'bar'.encode('utf-8'),
             '+TILrwJJFp5zhQzWFW3tAQbiu2rYyrAbe7vr5tEGUxc=')
        ]

        incorrect_hmac = [
            ('hello',
             'world'.encode('utf-8'),
             '+TILrwJJFp5zhQzWFW3tAQbiu2rYyrAbe7vr5tEGUxc='),
            ('bye',
             'bye'.encode('utf-8'),
             '8ayXAutfryPKKRpNxG3t3u4qeMza8KQSvtdxTP/7HMQ='),
            ('foo',
             'bar'.encode('utf-8'),
             'HHfaL+C4HxPTexmlKO9pwEHuAXkErAz85APGPOgvBVU=')
        ]

        for triplet in correct_hmac:
            self.assertTrue(hmac_is_valid(*triplet))

        for triplet in incorrect_hmac:
            self.assertFalse(hmac_is_valid(*triplet))


class SKULookupTest(TestCase):

    def test_sku_roundtrip(self):
        """When given a SKU that looks like a course ID, do we return it
        unchanged?"""
        sku = 'course-v1:org+course+run1'
        course_id = sku
        self.assertEqual(lookup_course_id(sku), course_id)

    def test_successful_lookup(self):
        """When given a SKU that resolves (via a redirect) to a course ID, do
        we return that course ID correctly?"""
        sku = 'course001'
        course_id = 'course-v1:org+course+run1'
        lookup_url = '%s/%s' % (settings.WEBHOOK_RECEIVER_LMS_BASE_URL,
                                sku)
        found_url = '%s/courses/%s/about' % (settings.WEBHOOK_RECEIVER_LMS_BASE_URL,  # noqa: E501
                                             course_id)

        with requests_mock.Mocker() as m:
            m.register_uri('HEAD',
                           lookup_url,
                           status_code=301,
                           headers={'Location': found_url})
            m.register_uri('HEAD',
                           found_url,
                           status_code=200)
            self.assertEqual(lookup_course_id(sku), course_id)

    def test_broken_redirect(self):
        """When given a SKU that resolves (via a redirect) to a non-existent
        URL, do we throw an HTTPError?"""
        sku = 'course001'
        course_id = 'course-v1:org+course+run1'
        lookup_url = '%s/%s' % (settings.WEBHOOK_RECEIVER_LMS_BASE_URL,
                                sku)
        found_url = '%s/courses/%s/about' % (settings.WEBHOOK_RECEIVER_LMS_BASE_URL,  # noqa: E501
                                             course_id)

        with requests_mock.Mocker() as m:
            m.register_uri('HEAD',
                           lookup_url,
                           status_code=301,
                           headers={'Location': found_url})
            m.register_uri('HEAD',
                           found_url,
                           status_code=404)
            with self.assertRaises(HTTPError):
                lookup_course_id(sku)

    def test_invalid_redirect(self):
        """When given a SKU that resolves (via a redirect) to a URL that
        exists but does not contain a course ID URL, do we throw a
        SKULookupException?
        """
        sku = 'course001'
        course_id = 'somebrokencourseid'
        lookup_url = '%s/%s' % (settings.WEBHOOK_RECEIVER_LMS_BASE_URL,
                                sku)
        found_url = '%s/courses/%s/about' % (settings.WEBHOOK_RECEIVER_LMS_BASE_URL,  # noqa: E501
                                             course_id)

        with requests_mock.Mocker() as m:
            m.register_uri('HEAD',
                           lookup_url,
                           status_code=301,
                           headers={'Location': found_url})
            m.register_uri('HEAD',
                           found_url,
                           status_code=200)
            with self.assertRaises(SKULookupException):
                lookup_course_id(sku)
