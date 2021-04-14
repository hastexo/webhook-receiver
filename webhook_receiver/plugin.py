"""
edX webhooks Django Plugin App settings.
"""

import os


def get_setting(settings, setting_key, default_val=None):
    """
    Retrieves the value of the requested setting

    Gets the Value of an Environment variable either from
    the OS Environment or from the settings ENV_TOKENS

    Arguments:
        - settings (dict): Django settings
        - setting_key (str): String
        - default_val (str): String

    Returns:
        - Value of the requested setting (String)
    """

    setting_val = os.environ.get(setting_key, default_val)

    if hasattr(settings, 'ENV_TOKENS'):
        return settings.ENV_TOKENS.get(setting_key, setting_val)

    return setting_val


def plugin_settings(settings):
    """
    Specifies django environment settings

    Extend django settings with the plugin defined ones to be able to
    configure the plugin individually.

    Arguments:
        settings (dict): Django settings

    Returns:
        None
    """

    settings.WEBHOOK_RECEIVER_LMS_BASE_URL = get_setting(
        settings,
        'LMS_BASE',
        default_val='http://localhost:18000'
    )

    settings.WEBHOOK_RECEIVER_EDX_OAUTH2_KEY = get_setting(
        settings,
        'WEBHOOK_RECEIVER_EDX_OAUTH2_KEY'
    )

    settings.WEBHOOK_RECEIVER_EDX_OAUTH2_SECRET = get_setting(
        settings,
        'WEBHOOK_RECEIVER_EDX_OAUTH2_SECRET'
    )

    settings.WEBHOOK_RECEIVER_SKU_PREFIX = get_setting(
        settings,
        'WEBHOOK_RECEIVER_SKU_PREFIX'
    )

    settings.WEBHOOK_RECEIVER_SETTINGS = {
        'shopify': {
            'shop_domain': get_setting(
                settings,
                'WEBHOOK_RECEIVER_SETTINGS_SHOPIFY_SHOP_DOMAIN'
            ),
            'api_key': get_setting(
                settings,
                'WEBHOOK_RECEIVER_SETTINGS_SHOPIFY_API_KEY'
            ),
        },
        'woocommerce': {
            'source': get_setting(
                settings,
                'WEBHOOK_RECEIVER_WOOCOMMERCE_SOURCE'
            ),
            'secret': get_setting(
                settings,
                'WEBHOOK_RECEIVER_WOOCOMMERCE_SECRET'
            ),
        },
    }
