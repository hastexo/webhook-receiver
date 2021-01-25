from .views import order_create

from django.urls import path

urlpatterns = [
    path('order/create',
         order_create,
         name='woocommerce_order_create'),
]
