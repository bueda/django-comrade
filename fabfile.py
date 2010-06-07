#!/usr/bin/env python
import os
from fabric.api import *
from fabric.contrib.console import confirm

from fab_shared import (_nose_test_runner, _test as test,
        _package_deploy as deploy)

env.unit = "django-comrade"
env.root_dir = os.path.abspath(os.path.dirname(__file__))
env.scm = env.root_dir
env.allow_no_tag = True
env.upload_to_s3 = True
env.test_runner = _nose_test_runner
