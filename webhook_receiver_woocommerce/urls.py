from .views import order_create_or_update

from django.urls import path

urlpatterns = [
    path('order/create',
         order_create_or_update,
         name='woocommerce_order_create'),
    path('order/update',
         order_create_or_update,
         name='woocommerce_order_update'),
]
