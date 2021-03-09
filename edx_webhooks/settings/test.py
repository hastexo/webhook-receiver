from . import *  # noqa: F401, F403

SECRET_KEY = 'not-so-secret pass phrase used for testing'

WEBHOOK_SETTINGS = {
    'edx_webhooks_shopify': {
        'shop_domain': 'example.com',
        'api_key': 'secret',
    },
    'edx_webhooks_woocommerce': {
        'source': 'https://example.com',
        'secret': 'secret',
    },
}
