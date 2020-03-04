from django.contrib import admin

from .views import order_create

try:
    from django.urls import path
    # Django >= 2.0
    urlpatterns = [
        path('shopify/order/create',
             order_create,
             name='shopify_order_create'),
        path('admin/',
             admin.site.urls),
    ]
except ImportError:
    from django.conf.urls import url
    # Django < 2.0
    urlpatterns = [
        url(r'^shopify/order/create',
            order_create,
            name='shopify_order_create'),
        url(r'^admin/',
            admin.site.urls),
    ]
