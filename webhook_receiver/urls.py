from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('webhooks/shopify/',
         include('webhook_receiver_shopify.urls')),
    path('webhooks/woocommerce/',
         include('webhook_receiver_woocommerce.urls')),
    path('admin/',
         admin.site.urls),
]
