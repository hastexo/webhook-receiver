from __future__ import unicode_literals
import environ
import os

from dotenv import load_dotenv

# Populate os.environ with variables from .env (if it exists)
load_dotenv(verbose=True)

# Now parse the pre-populated environment into django-environ
env = environ.Env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'webhook_receiver',
    'webhook_receiver_shopify',
    'webhook_receiver_woocommerce',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    },
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'

ROOT_URLCONF = 'webhook_receiver.urls'

# SECURITY WARNING: keep the secret key used in production secret!
# We're setting a default of None here as that will cause Django to
# refuse to start the key isn't set in the environment or in a config
# file.
SECRET_KEY = env.str('DJANGO_SECRET_KEY', default=None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=False)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s:%(name)s:%(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': env.str('DJANGO_LOG_LEVEL',
                         default='WARNING').upper(),
    },
}

# We populate ALLOWED_HOSTS from a comma-separated list. Running with
# DEBUG = True overrides this, and is equivalent to setting the
# DJANGO_ALLOWED_HOSTS envar to "localhost,127.0.0.1,[::1]".
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default="")

# Async task processing via Celery
CELERY_BROKER_URL = env.str('DJANGO_CELERY_BROKER_URL', default="")

# If the broker URL is empty, run Celery in always-eager mode. Define
# both ALWAYS_EAGER (Celery <4) and TASK_ALWAYS_EAGER (Celery >= 4).
CELERY_ALWAYS_EAGER = not bool(CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = not bool(CELERY_BROKER_URL)

DATABASES = {
    'default': env.db('DJANGO_DATABASE_URL',
                      default="sqlite://:memory:"),
}

CACHES = {
    'default': env.cache('DJANGO_CACHE_URL',
                         default="dummycache://"),
}

WEBHOOK_RECEIVER_EDX_OAUTH2_URL_ROOT = env.str(
    'DJANGO_WEBHOOK_RECEIVER_EDX_OAUTH2_URL_ROOT',
    default='http://localhost:18000')
WEBHOOK_RECEIVER_EDX_OAUTH2_KEY = env.str(
    'DJANGO_WEBHOOK_RECEIVER_EDX_OAUTH2_KEY',
    default='')
WEBHOOK_RECEIVER_EDX_OAUTH2_SECRET = env.str(
    'DJANGO_WEBHOOK_RECEIVER_EDX_OAUTH2_SECRET',
    default='')

WEBHOOK_RECEIVER_SETTINGS = {
    'shopify': {
        'shop_domain': env.str(
            'DJANGO_WEBHOOK_RECEIVER_SETTINGS_SHOPIFY_SHOP_DOMAIN',
            default=''),
        'api_key': env.str(
            'DJANGO_WEBHOOK_RECEIVER_SETTINGS_SHOPIFY_API_KEY',
            default=''),
    },
    'woocommerce': {
        'source': env.str(
            'DJANGO_WEBHOOK_RECEIVER_SETTINGS_WOOCOMMERCE_SOURCE',
            default=''),
        'secret': env.str(
            'DJANGO_WEBHOOK_RECEIVER_SETTINGS_WOOCOMMERCE_SECRET',
            default=''),
    },
}
