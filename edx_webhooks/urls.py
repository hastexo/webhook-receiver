from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('webhooks/shopify/', include('edx_shopify.urls')),
    path('webhooks/woocommerce/', include('edx_woocommerce.urls')),
    path('admin/', admin.site.urls),
]
