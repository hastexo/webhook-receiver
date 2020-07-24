# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from requests.exceptions import HTTPError

from edx_shopify.models import Order
from edx_shopify.tasks import process
from edx_shopify.utils import record_order

import requests_mock

from . import ShopifyTestCase


class ProcessOrderTest(ShopifyTestCase):

    def setUp(self):
        self.setup_payload()
        self.setup_requests()

    def test_invalid_sku(self):
        fixup_payload = self.raw_payload.decode('utf-8').replace("course-v1:org+course+run1",  # noqa: E501
                                                                 "course-v1:org+nosuchcourse+run1")  # noqa: E501
        fixup_json_payload = json.loads(fixup_payload)
        order, created = record_order(fixup_json_payload)

        result = None
        with requests_mock.Mocker() as m:
            m.register_uri('POST',
                           self.token_uri,
                           json=self.token_response)
            m.register_uri('POST',
                           self.enroll_uri,
                           status_code=400)
            with self.assertRaises(HTTPError):
                result = process.delay(fixup_json_payload)
                result.get(5)

        self.assertEqual(result.state, 'FAILURE')

        # Even with the exception raised, it's the task failure
        # handler's job to set the status to ERROR. Given the async
        # nature of the task, though, the object reference doesn't
        # learn of the update until we read back the order. This can't
        # just use refresh_from_db(), because of the FSM-protected
        # status field.
        order = Order.objects.get(pk=order.id)
        self.assertEqual(order.status, Order.ERROR)

    def test_valid_order(self):
        order, created = record_order(self.json_payload)

        result = None

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
            result = process.delay(self.json_payload)
            result.get(5)

        self.assertEqual(result.state, 'SUCCESS')

        # Read back the order (can't just use refresh_from_db(),
        # because of the FSM-protected status field)
        order = Order.objects.get(pk=order.id)
        self.assertEqual(order.status, Order.PROCESSED)
