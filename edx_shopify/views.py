from __future__ import unicode_literals

import logging
import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .utils import hmac_is_valid, record_order
from .models import Order
from .tasks import process


logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def order_create(request):
    # Load configuration
    conf = settings.WEBHOOK_SETTINGS['edx_shopify']

    # Process request
    try:
        hmac = request.META['HTTP_X_SHOPIFY_HMAC_SHA256']
    except KeyError:
        logger.error('Request is missing X-Shopify-Hmac-Sha256 header')
        return HttpResponse(status=400)

    try:
        shop_domain = request.META['HTTP_X_SHOPIFY_SHOP_DOMAIN']
    except KeyError:
        logger.error('Request is missing X-Shopify-Shop-Domain header')
        return HttpResponse(status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except ValueError:
        logger.error('Unable to parse request body as UTF-8 JSON')
        return HttpResponse(status=400)

    if (conf['shop_domain'] != shop_domain):
        logger.error('Unknown shop domain %s' % shop_domain)
        return HttpResponse(status=403)

    if (not hmac_is_valid(conf['api_key'],
                          request.body,
                          hmac)):
        logger.error('Failed to verify HMAC signature')
        return HttpResponse(status=403)

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
    if order.status == Order.UNPROCESSED:
        logger.info('Scheduling order %s for processing' % order.id)
        process.delay(data, send_email)
    else:
        logger.info('Order %s already processed, '
                    'nothing to do' % order.id)

    return HttpResponse(status=200)
