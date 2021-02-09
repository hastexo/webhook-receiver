from django.contrib import admin

from .models import ShopifyOrder, ShopifyOrderItem

admin.site.register(ShopifyOrder)
admin.site.register(ShopifyOrderItem)
