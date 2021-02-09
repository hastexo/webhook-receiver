from django.db.models import UniqueConstraint, ForeignKey, PROTECT

from edx_webhooks import models

APP_LABEL = 'edx_woocommerce'


class Order(models.Order):

    class Meta:
        app_label = APP_LABEL
        abstract = False


class OrderItem(models.OrderItem):

    class Meta:
        app_label = APP_LABEL
        abstract = False
        constraints = [
            UniqueConstraint(fields=['order', 'sku', 'email'],
                             name='unique_order_sku_email')
        ]

    order = ForeignKey(
        Order,
        on_delete=PROTECT
    )
