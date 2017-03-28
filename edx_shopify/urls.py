from django.conf.urls import url

from .views import order_create

urlpatterns = [url(r'^shopify/order/create',
                   order_create,
                   name='shopify_order_create'),
]
