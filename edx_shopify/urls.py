from django.contrib import admin

from .views import order_create

from django.urls import path

urlpatterns = [
    path('shopify/order/create',
         order_create,
         name='shopify_order_create'),
    path('admin/',
         admin.site.urls),
]
