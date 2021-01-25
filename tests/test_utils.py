from __future__ import unicode_literals

from django.test import TestCase
from edx_webhooks.utils import hmac_is_valid


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
