# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import base64
import hmac

from django.conf import settings
from django.test import Client

import requests_mock

from . import ShopifyTestCase


class TestOrderCreation(ShopifyTestCase):

    def setUp(self):
        self.setup_payload()
        self.setup_requests()

        # Set enforce_csrf_checks=True here because testing must still
        # work (webhooks are explicitly exempted from CSRF protection)
        self.client = Client(enforce_csrf_checks=True)

        conf = settings.WEBHOOK_SETTINGS['edx_shopify']

        # Calculate 3 SHA256 hashes over the payload, which the
        # webhook handler must verify and accept or reject: a correct
        # hash, a hash from the wrong (reversed) key, and a corrupted
        # hash containing an invalid base64 character.
        correct_hash = hmac.new(conf['api_key'].encode('utf-8'),
                                self.raw_payload,
                                hashlib.sha256).digest()
        incorrect_hash = hmac.new(conf['api_key'][::-1].encode('utf-8'),
                                  self.raw_payload,
                                  hashlib.sha256).digest()
        self.correct_signature = base64.b64encode(correct_hash).decode()
        self.incorrect_signature = base64.b64encode(incorrect_hash).decode()
        self.corrupt_signature = "-%s" % base64.b64encode(correct_hash)[1:].decode()  # noqa: E501

        # Set up a mock course
        self.setup_course()

    def test_invalid_method_put(self):
        response = self.client.put('/shopify/order/create',
                                   self.raw_payload,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_invalid_method_get(self):
        response = self.client.get('/shopify/order/create')
        self.assertEqual(response.status_code, 405)

    def test_missing_hmac_header(self):
        response = self.client.post('/shopify/order/create',
                                    self.raw_payload,
                                    HTTP_X_SHOPIFY_SHOP_DOMAIN='example.com',
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_missing_shop_domain_header(self):
        response = self.client.post('/shopify/order/create',
                                    self.raw_payload,
                                    HTTP_X_SHOPIFY_HMAC_SHA256=self.corrupt_signature,  # noqa: E501
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_incorrect_signature(self):
        response = self.client.post('/shopify/order/create',
                                    self.raw_payload,
                                    content_type='application/json',
                                    HTTP_X_SHOPIFY_HMAC_SHA256=self.incorrect_signature,  # noqa: E501
                                    HTTP_X_SHOPIFY_SHOP_DOMAIN='example.com')
        self.assertEqual(response.status_code, 403)

    def test_corrupt_signature(self):
        response = self.client.post('/shopify/order/create',
                                    self.raw_payload,
                                    content_type='application/json',
                                    HTTP_X_SHOPIFY_HMAC_SHA256=self.corrupt_signature,  # noqa: E501
                                    HTTP_X_SHOPIFY_SHOP_DOMAIN='example.com')
        self.assertEqual(response.status_code, 403)

    def test_corrupt_data(self):
        # Invalid JSON
        corrupt_payload = "{".encode('utf-8')

        response = self.client.post('/shopify/order/create',
                                    corrupt_payload,
                                    content_type='application/json',
                                    HTTP_X_SHOPIFY_HMAC_SHA256=self.correct_signature,  # noqa: E501
                                    HTTP_X_SHOPIFY_SHOP_DOMAIN='example.com')
        self.assertEqual(response.status_code, 400)

    def test_invalid_domain(self):
        response = self.client.post('/shopify/order/create',
                                    self.raw_payload,
                                    content_type='application/json',
                                    HTTP_X_SHOPIFY_HMAC_SHA256=self.correct_signature,  # noqa: E501
                                    HTTP_X_SHOPIFY_SHOP_DOMAIN='nonexistant-domain.com')  # noqa: E501
        self.assertEqual(response.status_code, 403)

    def test_valid_order(self):
        enrollment_response = {
            'action': 'enroll',
            'courses': {
                'course-v1:org+course+run1': {
                    'action': 'enroll',
                    'results': [
                        {
                            'identifier': 'learner@example.com',
                            'after': {
                                'enrollment': False,
                                'allowed': True,
                                'user': False,
                                'auto_enroll': True
                            },
                            'before': {
                                'enrollment': False,
                                'allowed': False,
                                'user': False,
                                'auto_enroll': False
                            }
                        }
                    ],
                    'auto_enroll': True}
            },
            'email_students': True,
            'auto_enroll': True
        }

        with requests_mock.Mocker() as m:
            m.register_uri('POST',
                           self.token_uri,
                           json=self.token_response)
            m.register_uri('POST',
                           self.enroll_uri,
                           json=enrollment_response)
            response = self.client.post('/shopify/order/create',
                                        self.raw_payload,
                                        content_type='application/json',
                                        HTTP_X_SHOPIFY_HMAC_SHA256=self.correct_signature,  # noqa: E501
                                        HTTP_X_SHOPIFY_SHOP_DOMAIN='example.com')  # noqa: E501
            self.assertEqual(response.status_code, 200)

    def test_valid_order_again(self):
        """Re-inject a previously processed order, so we can check
        idempotency of order processing."""

        self.test_valid_order()
        self.test_valid_order()
