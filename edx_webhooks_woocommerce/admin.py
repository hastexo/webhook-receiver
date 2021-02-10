from django.contrib import admin

from .models import WooCommerceOrder
from .models import WooCommerceOrderItem

admin.site.register(WooCommerceOrder)
admin.site.register(WooCommerceOrderItem)
