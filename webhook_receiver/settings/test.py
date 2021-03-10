from . import *  # noqa: F401, F403

SECRET_KEY = 'not-so-secret pass phrase used for testing'

WEBHOOK_RECEIVER_SETTINGS = {
    'webhook_receiver_shopify': {
        'shop_domain': 'example.com',
        'api_key': 'secret',
    },
    'webhook_receiver_woocommerce': {
        'source': 'https://example.com',
        'secret': 'secret',
    },
}
