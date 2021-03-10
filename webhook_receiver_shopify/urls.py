from .views import order_create

from django.urls import path

urlpatterns = [
    path('order/create',
         order_create,
         name='shopify_order_create'),
]
