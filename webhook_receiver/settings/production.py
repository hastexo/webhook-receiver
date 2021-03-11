import os

from yaml import load, SafeLoader
from yaml.scanner import ScannerError

from django.core.exceptions import ImproperlyConfigured

from . import *  # noqa: F403

# We inherit all settings from base.py, including the anything set in
# the environment.  However, if the environment contains the variable
# WEBHOOK_RECEIVER_CFG, we open that file and parse it as YAML, and
# anything we find there overrides any values previously set.  Thus,
# if we have conflicting settings in the environment and the config
# file, the config file prevails.
CONFIG_FILE = env.str('WEBHOOK_RECEIVER_CFG', None)  # noqa: F405
if CONFIG_FILE:
    try:
        with open(CONFIG_FILE) as f:
            config_from_yaml = load(f, Loader=SafeLoader)
            vars().update(config_from_yaml)
    except OSError as e:
        raise ImproperlyConfigured(e)
    except (ValueError, TypeError, ScannerError) as e:
        raise ImproperlyConfigured(
            'Unable to update configuration '
            'with contents of %s: %s' % (CONFIG_FILE, e)
        )

# The "make migrate" ("manage.py migrate") functionality needs to
# honour the DB_MIGRATION_ environment variables.
DB_OVERRIDES = dict(
    PASSWORD=os.environ.get('DB_MIGRATION_PASS',
                            DATABASES['default']['PASSWORD']),  # noqa: F405
    ENGINE=os.environ.get('DB_MIGRATION_ENGINE',
                          DATABASES['default']['ENGINE']),  # noqa: F405
    USER=os.environ.get('DB_MIGRATION_USER',
                        DATABASES['default']['USER']),  # noqa: F405
    NAME=os.environ.get('DB_MIGRATION_NAME',
                        DATABASES['default']['NAME']),  # noqa: F405
    HOST=os.environ.get('DB_MIGRATION_HOST',
                        DATABASES['default']['HOST']),  # noqa: F405
    PORT=os.environ.get('DB_MIGRATION_PORT',
                        DATABASES['default']['PORT']),  # noqa: F405
    OPTIONS=os.environ.get('DB_MIGRATION_OPTIONS',
                           DATABASES['default']['OPTIONS']),  # noqa: F405
)
for override, value in DB_OVERRIDES.items():
    DATABASES['default'][override] = value  # noqa: F405

# The one thing we don't allow to be set in production, neither from
# the environment nor from a config file, is DEBUG == True.
if DEBUG:  # noqa: F405
    msg = "Refusing to start with DEBUG enabled in production."
    raise ImproperlyConfigured(msg)
