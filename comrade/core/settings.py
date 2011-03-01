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

INTERNAL_IPS = ('127.0.0.1',)

# Logging

if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO
USE_SYSLOG = DEPLOYMENT != DeploymentType.SOLO

# Sessions

if DEPLOYMENT != DeploymentType.SOLO:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# CSRF Protection

CSRF_FAILURE_VIEW = 'comrade.views.simple.csrf_failure'

# Cache Backend

CACHE_TIMEOUT = 3600
MAX_CACHE_ENTRIES = 10000
CACHE_MIDDLEWARE_SECONDS = 3600
CACHE_MIDDLEWARE_KEY_PREFIX = ''
if DEPLOYMENT == DeploymentType.SOLO:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': '127.0.0.1:11211',
            'TIMEOUT': CACHE_TIMEOUT,
            'MAX_ENTRIES': MAX_CACHE_ENTRIES
        }
    }

DEFAULT_FROM_EMAIL = "Bueda <support@bueda.com>"
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
