from django.db.models import UniqueConstraint, ForeignKey
from django.db.models import PROTECT

from edx_webhooks.models import Order, OrderItem

APP_LABEL = 'edx_shopify'


class ShopifyOrder(Order):

    class Meta:
        app_label = APP_LABEL
        abstract = False


class ShopifyOrderItem(OrderItem):

    class Meta:
        app_label = APP_LABEL
        abstract = False
        constraints = [
            UniqueConstraint(fields=['order', 'sku', 'email'],
                             name='unique_order_sku_email')
        ]

    order = ForeignKey(
        ShopifyOrder,
        on_delete=PROTECT
    )
