import os
import logging

# Make filepaths relative to settings.
path = lambda root,*a: os.path.join(root, *a)

ADMINS = (
           ('Christopher Peplin', 'peplin@bueda.com'),
           ('Vasco Pedro', 'vasco@bueda.com'),
           ('Vignesh Murugesan','vignesh@bueda.com'),
           ('Ken Kochis', 'ken@bueda.com'),
)
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
    DEPLOYMENT = os.environ['DEPLOYMENT_TYPE']
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

# Version Information

if DEPLOYMENT == DeploymentType.SOLO:
    import subprocess
    GIT_COMMIT = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
        stdout=subprocess.PIPE).communicate()[0].strip()
    del subprocess
elif DEPLOYMENT != DeploymentType.PRODUCTION:
    GIT_COMMIT = "$Format:%h$"[:-1]
else:
    GIT_COMMIT = ""

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

# E-mail Server

if DEPLOYMENT != DeploymentType.SOLO:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'noreply@bueda.com'
    EMAIL_HOST_PASSWORD = 'feixieJ4'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = "Bueda Support <support@bueda.com>"
SERVER_EMAIL = "Bueda Operations <ops@bueda.com>"

# Internationalization

TIME_ZONE = 'America/Detroit'
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

