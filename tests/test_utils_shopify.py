from __future__ import unicode_literals

import json

from django.core.exceptions import ValidationError

from requests.exceptions import HTTPError

from webhook_receiver.models import JSONWebhookData

from webhook_receiver_shopify.utils import record_order
from webhook_receiver_shopify.utils import process_order, process_line_item
from webhook_receiver_shopify.models import ShopifyOrder as Order
from webhook_receiver_shopify.models import ShopifyOrderItem as OrderItem

import requests_mock

from . import ShopifyTestCase


class RecordOrderTest(ShopifyTestCase):

    def setUp(self):
        self.setup_payload()
        self.setup_webhook_data()

    def test_record_order(self):
        # Make sure the order gets created, and that its ID matches
        # that in the payload
        order1, created1 = record_order(self.webhook_data)
        self.assertTrue(created1)
        self.assertEqual(order1.id, self.json_payload['id'])
        # Try to create the order again, make sure we get a reference
        # instead
        order2, created2 = record_order(self.webhook_data)
        self.assertFalse(created2)
        self.assertEqual(order1, order2)


class ProcessOrderTest(ShopifyTestCase):

    def setUp(self):
        self.setup_payload()
        self.setup_webhook_data()
        self.setup_course()
        self.setup_requests()

    def test_valid_order(self):
        order, created = record_order(self.webhook_data)

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
            process_order(order, self.json_payload)

        self.assertEqual(order.status, Order.PROCESSED)

    def test_invalid_sku(self):
        fixup_payload = self.raw_payload.decode('utf-8').replace("course-v1:org+course+run1",  # noqa: E501
                                                                 "course-v1:org+nosuchcourse+run1")  # noqa: E501
        fixup_json_payload = json.loads(fixup_payload)
        fixup_webhook_data = JSONWebhookData(headers={},
                                             body=b'',
                                             content=fixup_json_payload)
        fixup_webhook_data.save()

        order, created = record_order(fixup_webhook_data)

        with requests_mock.Mocker() as m:
            m.register_uri('POST',
                           self.token_uri,
                           json=self.token_response)
            m.register_uri('POST',
                           self.enroll_uri,
                           status_code=404)
            # Non-existent course should raise a 404
            with self.assertRaises(HTTPError):
                process_order(order, fixup_json_payload)

        # At this stage, the order is still PROCESSING -- it's the
        # task failure handler's job to set the status to ERROR
        self.assertEqual(order.status, Order.PROCESSING)

    def test_valid_order_again(self):
        """Re-inject a previously processed order, so we can check
        idempotency of order processing."""
        self.test_valid_order()
        self.test_valid_order()


class ProcessLineItemTest(ShopifyTestCase):

    def setUp(self):
        self.setup_requests()

    def test_valid_single_line_item(self):
        order = Order()
        order.id = 40
        order.save()
        line_item = {
            "properties": [{"name": "email",
                            "value": "learner@example.com"}],
            "sku": "course-v1:org+course+run1"
        }

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

            order_item = process_line_item(order, line_item)

            # Read back the order item (can't just use
            # refresh_from_db(), because of the FSM-protected status
            # field)
            order_item = OrderItem.objects.get(pk=order_item.id)

            self.assertEqual(order_item.order, order)
            self.assertEqual(order_item.sku, 'course-v1:org+course+run1')
            self.assertEqual(order_item.email, 'learner@example.com')
            self.assertEqual(order_item.status, OrderItem.PROCESSED)

    def test_invalid_line_item(self):
        order = Order()
        order.id = 41
        order.save()
        line_items = [{"sku": "course-v1:org+nosuchcourse+run1"},
                      {"properties": [{"name": "email",
                                       "value": "learner@example.com"}]}]
        for line_item in line_items:
            with self.assertRaises(KeyError):
                process_line_item(order, line_item)

    def test_invalid_sku(self):
        order = Order()
        order.id = 42
        order.save()
        line_items = [{"properties": [{"name": "email",
                                       "value": "learner@example.com"}],
                       "sku": "course-v1:org+nosuchcourse+run1"}]
        for line_item in line_items:
            with requests_mock.Mocker() as m:
                # In the bulk enrollment API, an invalid course ID
                # results in an HTTP 404
                m.register_uri('POST',
                               self.token_uri,
                               json=self.token_response)
                m.register_uri('POST',
                               self.enroll_uri,
                               status_code=404)

                with self.assertRaises(HTTPError):
                    process_line_item(order, line_item)

    def test_invalid_email(self):
        order = Order()
        order.id = 43
        order.save()
        line_items = [{"properties": [{"name": "email",
                                       "value": "akjzcdfbgakugbfvkljzgh"}],
                       "sku": "course-v1:org+course+run1"}]
        for line_item in line_items:
            with self.assertRaises(ValidationError):
                process_line_item(order, line_item)
