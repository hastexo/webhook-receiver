# -*- coding: utf-8 -*-
import datetime
import warnings

from django.test import TestCase
from django.db import connection
from django.db import DatabaseError, IntegrityError

from edx_shopify.models import Order, OrderItem


class TestOrder(TestCase):

    model = Order

    def setUp(self):
        self.order = self.model()
        self.order.id = 1
        self.order.email = "johndoe@example.com"
        self.order.first_name = "John"
        self.order.last_name = "Doe"
        # self.order.received must be populated by default
        # self.order.status must be populated by default

    def test_default_status(self):
        # Does the order get a default status on creation?
        self.assertEqual(self.order.status, self.model.UNPROCESSED)

    def test_default_received(self):
        # Does the order get a default received date on creation?
        self.assertIsInstance(self.order.received, datetime.datetime)

    def test_save(self):
        # Can we save the order?
        self.order.save()


class TestOrderItem(TestCase):

    model = OrderItem

    def setUp(self):
        self.order_item = self.model()
        self.order = Order()
        self.order.id = 2
        self.order.email = "janedoe@example.com"
        self.order.first_name = "Jane"
        self.order.last_name = "Doe"
        self.order.save()

        self.order_item = self.model()
        self.order_item.order = self.order
        self.order_item.sku = "42MYPRODUCT"
        self.order_item.email = "daisydoe@example.com"
        # self.order_item.status must be populated by default

    def test_save(self):
        # Can we save a properly defined order item?
        self.order_item.save()

    def test_default_status(self):
        # Does the order get a default status on creation?
        self.assertEqual(self.order_item.status,
                         self.model.UNPROCESSED)

    def test_empty_order_reference(self):
        # Does removing the parent order from an order item raise an
        # error?
        # Django 1.8 raises a ValueError on setting the value in
        # memory. Django 1.10, however, flags an IntegrityError on
        # attempting to save the object (i.e. write it to the
        # database).
        with self.assertRaises((ValueError, IntegrityError)):
            self.order_item.order = None
            self.order_item.save()

    def test_same_order_same_email_different_sku(self):
        # Can we create an order item with the same order reference
        # and email, but a different SKU?
        second_order_item = self.model()
        second_order_item.order = self.order_item.order
        second_order_item.sku = "54MYOTHERPRODUCT"
        second_order_item.email = self.order_item.email
        second_order_item.save()

    def test_same_order_different_email_same_sku(self):
        # Can we create an order item with the same order reference
        # and SKU, but a different email?
        second_order_item = self.model()
        second_order_item.order = self.order
        second_order_item.sku = self.order_item.sku
        second_order_item.email = "ericdoe@example.com"
        second_order_item.save()

    def test_same_order_same_email_same_sku(self):
        # Do we fail to create an order item with the same order
        # reference, SKU, and email?
        #
        # Note: the unique_together constraint is enforced at the
        # database level. The sqlite3 backend does not support it.
        second_order_item = self.model()
        second_order_item.order = self.order_item.order
        second_order_item.sku = self.order_item.sku
        second_order_item.email = self.order_item.email
        if connection.vendor in ['sqlite']:
            warnings.warn("Unable to test for unique_together "
                          "constraint enforcement with %s" % connection.vendor)
        else:
            with self.assertRaises(DatabaseError):
                second_order_item.save()
