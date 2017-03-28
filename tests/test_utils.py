import json

from django.test import TestCase
from django.http import Http404
from django.core.exceptions import ValidationError

# We need this in order to mock.patch get_course_by_id
from edx_shopify import utils

# We also import these for convenience
from edx_shopify.utils import hmac_is_valid, record_order
from edx_shopify.utils import auto_enroll_email
from edx_shopify.utils import process_order, process_line_item

from edx_shopify.models import Order, OrderItem

from . import ShopifyTestCase

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class SignatureVerificationTest(TestCase):

    def test_hmac_is_valid(self):
        correct_hmac = [
            ('hello', 'world', '8ayXAutfryPKKRpNxG3t3u4qeMza8KQSvtdxTP/7HMQ='),
            ('bye', 'bye', 'HHfaL+C4HxPTexmlKO9pwEHuAXkErAz85APGPOgvBVU='),
            ('foo', 'bar', '+TILrwJJFp5zhQzWFW3tAQbiu2rYyrAbe7vr5tEGUxc=')
        ]

        incorrect_hmac = [
            ('hello', 'world', '+TILrwJJFp5zhQzWFW3tAQbiu2rYyrAbe7vr5tEGUxc='),
            ('bye', 'bye', '8ayXAutfryPKKRpNxG3t3u4qeMza8KQSvtdxTP/7HMQ='),
            ('foo', 'bar', 'HHfaL+C4HxPTexmlKO9pwEHuAXkErAz85APGPOgvBVU=')
        ]

        for triplet in correct_hmac:
            self.assertTrue(hmac_is_valid(*triplet))

        for triplet in incorrect_hmac:
            self.assertFalse(hmac_is_valid(*triplet))


class RecordOrderTest(ShopifyTestCase):

    def setUp(self):
        self.setup_payload()

    def test_record_order(self):
        # Make sure the order gets created, and that its ID matches
        # that in the payload
        order1, created1 = record_order(self.json_payload)
        self.assertTrue(created1)
        self.assertEqual(order1.id, self.json_payload['id'])
        # Try to create the order again, make sure we get a reference
        # instead
        order2, created2 = record_order(self.json_payload)
        self.assertFalse(created2)
        self.assertEqual(order1, order2)


class ProcessOrderTest(ShopifyTestCase):

    def setUp(self):
        self.setup_payload()
        self.setup_course()

    def test_valid_order(self):
        order, created = record_order(self.json_payload)

        mock_get_course_by_id = Mock(return_value=self.course)
        mock_get_email_params = Mock(return_value=self.email_params)
        mock_enroll_email = Mock()
        with patch.multiple(utils,
                            get_course_by_id=mock_get_course_by_id,
                            get_email_params=mock_get_email_params,
                            enroll_email=mock_enroll_email):
            process_order(order, self.json_payload)

        self.assertEqual(order.status, Order.PROCESSED)

    def test_invalid_sku(self):
        # Make sure the order gets created, and that its ID matches
        # that in the payload
        fixup_payload = self.raw_payload.replace("course-v1:org+course+run1",
                                                 "course-v1:org+nosuchcourse+run1")  # noqa: E501
        fixup_json_payload = json.loads(fixup_payload)
        order, created = record_order(fixup_json_payload)

        # Non-existent course should raise a 404
        with self.assertRaises(Http404):
            process_order(order, fixup_json_payload)

        # At this stage, the order is still PROCESSING -- it's the
        # task failure handler's job to set the status to ERROR
        self.assertEqual(order.status, Order.PROCESSING)


class ProcessLineItemTest(ShopifyTestCase):

    def setUp(self):
        self.setup_course()

    def test_valid_single_line_item(self):
        order = Order()
        order.id = 40
        order.save()
        line_items = [{"properties": [{"name": "email",
                                       "value": "learner@example.com"}],
                       "sku": "course-v1:org+course+run1"}]
        mock_get_course_by_id = Mock(return_value=self.course)
        mock_get_email_params = Mock(return_value=self.email_params)
        mock_enroll_email = Mock()
        for line_item in line_items:
            with patch.multiple(utils,
                                get_course_by_id=mock_get_course_by_id,
                                get_email_params=mock_get_email_params,
                                enroll_email=mock_enroll_email):
                order_item = process_line_item(order, line_item)

                # Did we mock-fetch the course with the correct locator?
                mock_get_course_by_id.assert_called_once_with(self.ck)

                # Did we mock-fetch the email params for the course
                # identified by that locator?
                mock_get_email_params.assert_called_once_with(self.course,
                                                              True,
                                                              secure=True)

                # Did we mock-invoke enroll_email with the correct parameters?
                mock_enroll_email.assert_called_once_with(self.ck,
                                                          'learner@example.com',  # noqa: E501
                                                          auto_enroll=True,
                                                          email_students=True,
                                                          email_params=self.email_params,  # noqa: E501
                                                          language=None)

                # Read back the order item
                order_item.refresh_from_db()
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
            with self.assertRaises(Http404):
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


class EmailEnrollmentTest(ShopifyTestCase):

    def setUp(self):
        self.setup_course()

    def test_enrollment_failure(self):
        # Enrolling in a non-existent course (or run) should fail, no
        # matter whether the user exists or not
        with self.assertRaises(Http404):
            auto_enroll_email('course-v1:org+nosuchcourse+run1',
                              'learner@example.com')
            auto_enroll_email('course-v1:org+course+nosuchrun',
                              'learner@example.com')
            auto_enroll_email('course-v1:org+nosuchcourse+run1',
                              'johndoe@example.com')

    def test_enrollment_success(self):
        mock_get_course_by_id = Mock(return_value=self.course)
        mock_get_email_params = Mock(return_value=self.email_params)
        mock_enroll_email = Mock()
        address = 'johndoe@example.com'

        with patch.multiple(utils,
                            get_course_by_id=mock_get_course_by_id,
                            get_email_params=mock_get_email_params,
                            enroll_email=mock_enroll_email):
            auto_enroll_email(self.course_id_string,
                              'johndoe@example.com',
                              send_email=False)

            # Did we mock-fetch the course with the correct locator?
            mock_get_course_by_id.assert_called_once_with(self.ck)

            # Did we mock-invoke enroll_email with the correct parameters?
            mock_enroll_email.assert_called_once_with(self.ck,
                                                      address,
                                                      auto_enroll=True,
                                                      email_students=False,
                                                      email_params=None,
                                                      language=None)

    def test_enrollment_success_with_email(self):
        mock_get_course_by_id = Mock(return_value=self.course)
        mock_get_email_params = Mock(return_value=self.email_params)
        mock_enroll_email = Mock()
        address = 'johndoe@example.com'

        with patch.multiple(utils,
                            get_course_by_id=mock_get_course_by_id,
                            get_email_params=mock_get_email_params,
                            enroll_email=mock_enroll_email):
            auto_enroll_email(self.course_id_string,
                              address,
                              send_email=True)

            # Did we mock-fetch the course with the correct locator?
            mock_get_course_by_id.assert_called_once_with(self.ck)

            # Did we mock-fetch the email params for the course
            # identified by that locator?
            mock_get_email_params.assert_called_once_with(self.course,
                                                          True,
                                                          secure=True)

            # Did we mock-invoke enroll_email with the correct parameters?
            mock_enroll_email.assert_called_once_with(self.ck,
                                                      address,
                                                      auto_enroll=True,
                                                      email_students=True,
                                                      email_params=self.email_params,  # noqa: E501
                                                      language=None)
