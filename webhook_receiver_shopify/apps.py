"""
edX webhooks Django app configuration for Shopify integration.
"""

from django.apps import AppConfig


class WebhookReceiverShopifyConfig(AppConfig):
    """
    Configuration for the Shopify integration as an edX Django Plugin App.
    Django Plugin App configuration to be able to use the module as a standalone edX Plugin App.
    """

    name = "webhook_receiver_shopify"
    plugin_app = {}
