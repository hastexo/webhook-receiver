"""
edX receiver Django app configuration.
"""

from django.apps import AppConfig


class WebhookReceiverConfig(AppConfig):
    """
    Configuration for the webhook receiver integration as an edX Django
    Plugin App. Django Plugin App configuration to be able to use the module
    as a standalone edX Plugin App.
    """

    name = "webhook_receiver"
    plugin_app = {
        "url_config": {
            "lms.djangoapp": {
                "namespace": "webhook_receiver",
            },
        },
        "settings_config": {
            "lms.djangoapp": {
                "common": {
                    "relative_path": "plugin"
                },
                "devstack": {
                    "relative_path": "plugin"
                },
                "production": {
                    "relative_path": "plugin"
                }
            }
        }
    }
