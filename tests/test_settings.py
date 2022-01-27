import os

from importlib import reload
from django.test import SimpleTestCase
from unittest.mock import patch

from webhook_receiver import settings as default_settings
from webhook_receiver.settings import production as production_settings


def mockenv(**envars):
    """A mock.patch decorator (or context manager) that injects
    custom values into os.environ"""
    return patch.dict(os.environ, envars)


class DefaultSettingsTest(SimpleTestCase):
    """Tests for default settings (webhook_receiver.settings)

    This class inherits from SimpleTestCase, rather than TestCase: the
    latter mangles the database settings for testing purposes. We
    don't want that here, since one of the things we're testing is
    precisely those database settings.
    """

    def setUp(self):
        # Make sure we reload the module at the start of the test run
        self.settings = reload(default_settings)

    def test_default_db_settings(self):
        default_db = self.settings.DATABASES['default']
        self.assertEqual(default_db['HOST'], '')
        self.assertEqual(default_db['PORT'], '')
        self.assertEqual(
            default_db['ENGINE'],
            'django.db.backends.sqlite3'
        )
        self.assertEqual(default_db['NAME'], ':memory:')
        self.assertEqual(default_db['USER'], '')
        self.assertEqual(default_db['PASSWORD'], '')
        self.assertEqual(default_db['OPTIONS'], {})


class ProductionSettingsTest(DefaultSettingsTest):
    """Tests for production settings (webhook_receiver.settings.production)

    This class runs all tests for default settings, albeit with the
    production configuration. Any test methods that should behave
    differently from the default settings should be overriden here."""

    def setUp(self):
        # Make sure we reload the module at the start of the test run
        self.settings = reload(production_settings)

    def test_db_overrides(self):
        # Absent any environment variables, DB_OVERRIDES should not
        # change the default database settings
        default_db = self.settings.DATABASES['default']
        db_overrides = self.settings.DB_OVERRIDES
        for key in ['NAME', 'HOST', 'PORT', 'ENGINE', 'USER',
                    'PASSWORD', 'OPTIONS']:
            if db_overrides[key]:
                self.assertEqual(default_db[key], db_overrides[key])


class ProductionSettingsWithOverrideTest(ProductionSettingsTest):
    """Tests for production settings with DB_MIGRATION_* overrides."""

    @mockenv(DB_MIGRATION_HOST='migrationhost',
             DB_MIGRATION_PASS='migrationpass',
             DB_MIGRATION_USER='migrationuser',
             DB_MIGRATION_NAME='migration',
             DB_MIGRATION_PORT='3306',
             DB_MIGRATION_ENGINE='django.db.backends.mysql',
             DB_MIGRATION_OPTIONS='{"foo": "bar"}')
    def test_default_db_settings(self):
        # We need to reload the settings here again. Mock patch
        # decorators will only patch test_ methods, so we can't do
        # this in setUp().
        self.settings = reload(production_settings)
        default_db = self.settings.DATABASES['default']
        self.assertEqual(default_db['HOST'], 'migrationhost')
        self.assertEqual(default_db['PORT'], '3306')
        self.assertEqual(
            default_db['ENGINE'],
            'django.db.backends.mysql'
        )
        self.assertEqual(default_db['NAME'], 'migration')
        self.assertEqual(default_db['USER'], 'migrationuser')
        self.assertEqual(default_db['PASSWORD'], 'migrationpass')
        self.assertDictEqual(default_db['OPTIONS'], {'foo': 'bar'})
