"""
edX webhooks Django app configuration for Woocommerce integration.
"""

from django.apps import AppConfig


class WebhookReceiverWoocommerceConfig(AppConfig):
    """
    Configuration for the Woocommerce integration as an edX Django Plugin App.
    Django Plugin App configuration to be able to use the module as a standalone edX Plugin App.
    """

    name = "webhook_receiver_woocommerce"
    plugin_app = {}
