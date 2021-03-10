from . import *  # noqa: F401, F403

SECRET_KEY = 'not-so-secret pass phrase used for testing'

WEBHOOK_RECEIVER_SETTINGS = {
    'shopify': {
        'shop_domain': 'example.com',
        'api_key': 'secret',
    },
    'woocommerce': {
        'source': 'https://example.com',
        'secret': 'secret',
    },
}
