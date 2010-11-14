import os
import logging

# Make filepaths relative to settings.
path = lambda root,*a: os.path.join(root, *a)

ADMINS = ()
MANAGERS = ADMINS

# Deployment Configuration

class DeploymentType:
    PRODUCTION = "PRODUCTION"
    DEV = "DEV"
    SOLO = "SOLO"
    STAGING = "STAGING"
    dict = {
        SOLO: 1,
        PRODUCTION: 2,
        DEV: 3,
        STAGING: 4
    }

if 'DEPLOYMENT_TYPE' in os.environ:
    DEPLOYMENT = os.environ['DEPLOYMENT_TYPE'].upper()
else:
    DEPLOYMENT = DeploymentType.SOLO

SITE_ID = DeploymentType.dict[DEPLOYMENT]

DEBUG = DEPLOYMENT != DeploymentType.PRODUCTION
STATIC_MEDIA_SERVER = DEPLOYMENT == DeploymentType.SOLO
TEMPLATE_DEBUG = DEBUG
SSL_ENABLED = DEBUG

INTERNAL_IPS = ('127.0.0.1',)

# Logging

if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO
USE_SYSLOG = DEPLOYMENT != DeploymentType.SOLO

# Cache Backend

CACHE_TIMEOUT = 60
MAX_CACHE_ENTRIES = 10000
CACHE_MIDDLEWARE_SECONDS = 3600
CACHE_MIDDLEWARE_KEY_PREFIX = ''
if DEPLOYMENT == DeploymentType.SOLO:
    CACHE_BACKEND = ('locmem://?timeout=%(CACHE_TIMEOUT)d'
            '&max_entries=%(MAX_CACHE_ENTRIES)d' % locals())
else:
    CACHE_BACKEND = ('memcached://127.0.0.1:11211/?timeout=%(CACHE_TIMEOUT)d'
            '&max_entries=%(MAX_CACHE_ENTRIES)d' % locals())

DEFAULT_FROM_EMAIL = "Bueda Support <support@bueda.com>"
SERVER_EMAIL = "Bueda Operations <ops@bueda.com>"

CONTACT_EMAIL = 'support@bueda.com'

# Internationalization

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
USE_I18N = False

# Templates

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

if DEPLOYMENT != DeploymentType.SOLO:
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS),
    )

ROOT_URLCONF = 'urls'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

DEVSERVER_MODULES = (
    'devserver.modules.sql.SQLRealTimeModule',
    'devserver.modules.sql.SQLSummaryModule',
    'devserver.modules.profile.ProfileSummaryModule',

    'devserver.modules.ajax.AjaxDumpModule',
    'devserver.modules.cache.CacheSummaryModule',
)
