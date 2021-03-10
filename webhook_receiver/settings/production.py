from yaml import load, SafeLoader
from yaml.scanner import ScannerError

from django.core.exceptions import ImproperlyConfigured

from . import *  # noqa: F403

# We inherit all settings from base.py, including the anything set in
# the environment.  However, if the environment contains the variable
# WEBHOOKS_CFG, we open that file and parse it as YAML, and anything
# we find there overrides any values previously set.  Thus, if we have
# conflicting settings in the environment and the config file, the
# config file prevails.
CONFIG_FILE = env.str('WEBHOOKS_CFG', None)  # noqa: F405
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

# The one thing we don't allow to be set in production, neither from
# the environment nor from a config file, is DEBUG == True.
if DEBUG:  # noqa: F405
    msg = "Refusing to start with DEBUG enabled in production."
    raise ImproperlyConfigured(msg)
