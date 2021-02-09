from django.db.models import UniqueConstraint, ForeignKey
from django.db.models import PROTECT

from edx_webhooks.models import Order, OrderItem

APP_LABEL = 'edx_woocommerce'


class WooCommerceOrder(Order):

    class Meta:
        app_label = APP_LABEL
        abstract = False


class WooCommerceOrderItem(OrderItem):

    class Meta:
        app_label = APP_LABEL
        abstract = False
        constraints = [
            UniqueConstraint(fields=['order', 'sku', 'email'],
                             name='unique_order_sku_email')
        ]

    order = ForeignKey(
        WooCommerceOrder,
        on_delete=PROTECT
    )
