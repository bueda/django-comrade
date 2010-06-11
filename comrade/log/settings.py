import logging, logging.handlers
import os.path
import types

try:
    from django.conf import settings
except ImportError, e:
    import os
    SETTINGS_MODULE = os.environ['SETTINGS_MODULE']
    settings = __import__(SETTINGS_MODULE)

from comrade.log import dictconfig

# Pulled from commonware.log we don't have to import that, which drags with
# it Django dependencies.
class RemoteAddressFormatter(logging.Formatter):
    """Formatter that makes sure REMOTE_ADDR is available."""

    def format(self, record):
        if ('%(REMOTE_ADDR)' in self._fmt
                and 'REMOTE_ADDR' not in record.__dict__):
            record.__dict__['REMOTE_ADDR'] = None
        return logging.Formatter.format(self, record)

class UTF8SafeFormatter(RemoteAddressFormatter):
    def __init__(self, fmt=None, datefmt=None, encoding='utf-8'):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.encoding = encoding
    
    def formatException(self, e):
        r = logging.Formatter.formatException(self, e)
        if type(r) in [types.StringType]:
            r = r.decode(self.encoding, 'replace') # Convert to unicode
        return r
    
    def format(self, record):
        t = RemoteAddressFormatter.format(self, record)
        if type(t) in [types.UnicodeType]:
            t = t.encode(self.encoding, 'replace')
        return t

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

if os.path.exists('/dev/log'):
    syslog_device = '/dev/log'
elif os.path.exists('/var/run/syslog'):
    syslog_device = '/var/run/syslog'

base_fmt = ('%(name)s:%(levelname)s %(message)s:%(pathname)s:%(lineno)s')

cfg = {
    'version': 1,
    'filters': {},
    'formatters': {
        'debug': {
            '()': UTF8SafeFormatter,
            'datefmt': '%H:%M:%s',
            'format': '%(asctime)s ' + base_fmt,
        },
        'prod': {
            '()': UTF8SafeFormatter,
            'datefmt': '%H:%M:%s',
            'format': '%s: [%%(REMOTE_ADDR)s] %s' % (settings.SYSLOG_TAG,
                                                     base_fmt),
        },
    },
    'handlers': {
        'console': {
            '()': logging.StreamHandler,
            'formatter': 'debug',
        },
        'null': {
            '()': NullHandler,
        },
        'syslog': {
            '()': logging.handlers.SysLogHandler,
            'facility': settings.SYSLOG_FACILITY,
            'address': syslog_device,
            'formatter': 'prod',
        },
    },
    'loggers': {
    },
    'root': {},
}

for key, value in settings.LOGGING.items():
    cfg[key].update(value)

# Set the level and handlers for all loggers.
for logger in cfg['loggers'].values() + [cfg['root']]:
    if 'handlers' not in logger:
        logger['handlers'] = ['syslog' if settings.USE_SYSLOG else 'console']
    if 'level' not in logger:
        logger['level'] = settings.LOG_LEVEL
    if logger is not cfg['root'] and 'propagate' not in logger:
        logger['propagate'] = False

dictconfig.dictConfig(cfg)
