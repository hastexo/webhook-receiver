from . import *  # noqa: F401, F403

SECRET_KEY = 'not-so-secret pass phrase used for testing'

ALLOWED_HOSTS = ['127.0.0.1', '::1']

WEBHOOK_RECEIVER_SETTINGS = {
    'shopify': {
        'shop_domain': 'example.com',
        'api_key': 'secret',
    },
    'woocommerce': {
        'source': 'https://example.com',
        'secret': 'secret',
        'require_payment': True,
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)s '
                      '[%(name)s] %(filename)s:%(lineno)d - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
