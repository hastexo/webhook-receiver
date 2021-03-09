import os
from os.path import abspath, dirname
from sys import path

SITE_ROOT = dirname(dirname(abspath(__file__)))
path.append(SITE_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webhooks.settings.local")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
