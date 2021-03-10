from __future__ import unicode_literals

import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from webhook_receiver.utils import receive_json_webhook, hmac_is_valid
from webhook_receiver.utils import fail_and_save, finish_and_save

from .utils import record_order
from .models import Order
from .tasks import process


logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def order_create(request):
    # Load configuration
    conf = settings.WEBHOOK_RECEIVER_SETTINGS['shopify']

    try:
        data = receive_json_webhook(request)
    except Exception:
        return HttpResponse(status=400)

    try:
        shop_domain = data.headers['X-Shopify-Shop-Domain']
    except KeyError:
        logger.error('Request is missing X-Shopify-Shop-Domain header')
        fail_and_save(data)
        return HttpResponse(status=400)

    if (conf['shop_domain'] != shop_domain):
        logger.error('Unknown shop domain %s' % shop_domain)
        fail_and_save(data)
        return HttpResponse(status=403)

    try:
        hmac = data.headers['X-Shopify-Hmac-Sha256']
    except KeyError:
        logger.error('Request is missing X-Shopify-Hmac-Sha256 header')
        fail_and_save(data)
        return HttpResponse(status=400)

    if (not hmac_is_valid(conf['api_key'],
                          data.body,
                          hmac)):
        logger.error('Failed to verify HMAC signature')
        fail_and_save(data)
        return HttpResponse(status=403)

    finish_and_save(data)

    # Record order
    order, created = record_order(data)
    if created:
        logger.info('Created order %s' % order.id)
    else:
        logger.info('Retrieved order %s' % order.id)

    send_email = True
    try:
        send_email = conf['send_email']
    except KeyError:
        pass

    # Process order
    if order.status == Order.NEW:
        logger.info('Scheduling order %s for processing' % order.id)
        process.delay(data.content, send_email)
    else:
        logger.info('Order %s already processed, '
                    'nothing to do' % order.id)

    return HttpResponse(status=200)
