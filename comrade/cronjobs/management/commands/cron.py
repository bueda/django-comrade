import sys
from django.conf import settings
from django.core.management.base import BaseCommand

from comrade import cronjobs

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run a script, often a cronjob'
    args = '[name args...]'

    def handle(self, *args, **opts):
        # Load up all the cron scripts.
        for app in settings.INSTALLED_APPS:
            try:
                __import__('%s.cron' % app)
            except ImportError:
                pass

        registered = cronjobs.registered

        if not args:
            logger.error("Cron called but doesn't know what to do.")
            print 'Try one of these: %s' % ', '.join(registered)
            sys.exit(1)

        script, args = args[0], args[1:]
        if script not in registered:
            logger.error("Cron called with unrecognized command: %s %s"
                    % (script, args))
            print 'Unrecognized name: %s' % script
            sys.exit(1)

        logger.info("Beginning job: %s %s" % (script, args))
        registered[script](*args)
        logger.info("Ending job: %s %s" % (script, args))
