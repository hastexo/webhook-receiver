from __future__ import unicode_literals

import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .utils import hmac_is_valid, record_order
from .models import Order
from .tasks import process


@csrf_exempt
@require_POST
def order_create(request):
    # Load configuration
    conf = settings.WEBHOOK_SETTINGS['edx_shopify']

    # Process request
    try:
        hmac = request.META['HTTP_X_SHOPIFY_HMAC_SHA256']
        shop_domain = request.META['HTTP_X_SHOPIFY_SHOP_DOMAIN']
        data = json.loads(request.body.decode('utf-8'))
    except (KeyError, ValueError):
        return HttpResponse(status=400)

    if ((not hmac_is_valid(conf['api_key'],
                           request.body,
                           hmac)) or (conf['shop_domain'] != shop_domain)):
        return HttpResponse(status=403)

    # Record order
    order, created = record_order(data)

    send_email = True
    try:
        send_email = conf['send_email']
    except KeyError:
        pass

    # Process order
    if order.status == Order.UNPROCESSED:
        process.delay(data, send_email)

    return HttpResponse(status=200)
