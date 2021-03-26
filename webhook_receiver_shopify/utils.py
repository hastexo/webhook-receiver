from __future__ import unicode_literals

import logging

from django.db import transaction

from webhook_receiver.utils import enroll_in_course, lookup_course_id

from .models import ShopifyOrder as Order
from .models import ShopifyOrderItem as OrderItem


logger = logging.getLogger(__name__)


def record_order(data):
    return Order.objects.get_or_create(
        id=data.content['id'],
        defaults={
            'webhook': data,
            'email': data.content['customer']['email'],
            'first_name': data.content['customer']['first_name'],
            'last_name': data.content['customer']['last_name']
        }
    )


def process_order(order, data, send_email=False):
    if order.status == Order.PROCESSED:
        logger.warning('Order %s has already '
                       'been processed, ignoring' % order.id)
        return
    elif order.status == Order.ERROR:
        logger.warning('Order %s has previously '
                       'failed to process, ignoring' % order.id)
        return

    if order.status == Order.PROCESSING:
        logger.warning('Order %s is already '
                       'being processed, retrying' % order.id)
    else:
        # Start processing the order. A concurrent attempt to access the
        # same order will result in django_fsm.ConcurrentTransition on
        # save(), causing a rollback.
        order.start_processing()
        with transaction.atomic():
            order.save()

    # Process line items
    for item in data['line_items']:
        # Process the line item. If the enrollment throws
        # an exception, we throw that exception up the stack so we can
        # attempt to retry order processing.
        process_line_item(order, item)
        logger.debug('Successfully processed line item '
                     '%s for order %s' % (item, order.id))

    # Mark the order status
    order.finish_processing()
    with transaction.atomic():
        order.save()

    return order


def process_line_item(order, item):
    """Process a line item of an order.

    Extract sku and properties.email, create an OrderItem, create an
    enrollment, and mark the OrderItem as processed. Propagate any
    errors, to be handled up the stack.
    """

    # Fetch relevant fields from the item
    sku = item['sku']
    email = next(
        p['value'] for p in item['properties']
        if p['name'] == 'email'
    )

    # Store line item, prop
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        sku=sku,
        email=email
    )

    if order_item.status == OrderItem.PROCESSED:
        logger.warning('Order item %s has already '
                       'been processed, ignoring' % order_item.id)
        return
    elif order_item.status == OrderItem.PROCESSING:
        logger.warning('Order item %s is already '
                       'being processed, retrying' % order_item.id)
    else:
        order_item.start_processing()
        with transaction.atomic():
            order_item.save()

    # Create an enrollment for the line item. If the enrollment throws
    # an exception, we throw that exception up the stack so we can
    # attempt to retry order processing.
    course_id = lookup_course_id(sku)
    enroll_in_course(course_id, email)

    # Mark the item as processed
    order_item.finish_processing()
    with transaction.atomic():
        order_item.save()

    return order_item
