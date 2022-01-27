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
    PASSWORD=env.str('DB_MIGRATION_PASS',  # noqa: F405
                     default=DATABASES['default']['PASSWORD']),  # noqa: F405
    ENGINE=env.str('DB_MIGRATION_ENGINE',  # noqa: F405
                   default=DATABASES['default']['ENGINE']),  # noqa: F405
    USER=env.str('DB_MIGRATION_USER',  # noqa: F405
                 default=DATABASES['default']['USER']),  # noqa: F405
    NAME=env.str('DB_MIGRATION_NAME',  # noqa: F405
                 default=DATABASES['default']['NAME']),  # noqa: F405
    HOST=env.str('DB_MIGRATION_HOST',  # noqa: F405
                 default=DATABASES['default']['HOST']),  # noqa: F405
    PORT=env.str('DB_MIGRATION_PORT',  # noqa: F405
                 default=DATABASES['default']['PORT']),  # noqa: F405
    OPTIONS=env.json(  # noqa: F405
        'DB_MIGRATION_OPTIONS',
        default=DATABASES['default'].get('OPTIONS', {})),  # noqa: F405
)
for override, value in DB_OVERRIDES.items():
    DATABASES['default'][override] = value  # noqa: F405

# The one thing we don't allow to be set in production, neither from
# the environment nor from a config file, is DEBUG == True.
if DEBUG:  # noqa: F405
    msg = "Refusing to start with DEBUG enabled in production."
    raise ImproperlyConfigured(msg)
