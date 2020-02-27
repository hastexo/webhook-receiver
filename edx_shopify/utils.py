import hashlib
import base64
import hmac
import logging

from edx_webhooks.utils import enroll_in_course

from .models import Order, OrderItem


def hmac_is_valid(key, msg, hmac_to_verify):
    hash = hmac.new(str(key), str(msg), hashlib.sha256)
    hmac_calculated = base64.b64encode(hash.digest())
    return hmac.compare_digest(hmac_calculated, hmac_to_verify)


def record_order(data):
    return Order.objects.get_or_create(
        id=data['id'],
        defaults={
            'email': data['customer']['email'],
            'first_name': data['customer']['first_name'],
            'last_name': data['customer']['last_name']
        }
    )


def process_order(order, data, send_email=False, logger=None):
    if not logger:
        logger = logging

    # If the order is anything but UNPROCESSED, abandon the attempt.
    if order.status != Order.UNPROCESSED:
        logger.warning('Order %s has already '
                       'been processed, ignoring' % order.id)
        return

    # Mark the order as being processed.
    order.status = Order.PROCESSING
    order.save()

    # Process line items
    for item in data['line_items']:
        process_line_item(order, item)
        logger.debug('Successfully processed line item '
                     '%s for order %s' % (item, order.id))

    # Mark the order status
    order.status = Order.PROCESSED
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

    # Create an enrollment for the line item
    if order_item.status == OrderItem.UNPROCESSED:
        enroll_in_course(sku, email)

    # Mark the item as processed
    order_item.status = OrderItem.PROCESSED
    order_item.save()

    return order_item
