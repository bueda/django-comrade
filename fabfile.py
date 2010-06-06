#!/usr/bin/env python
import os
from fabric.api import *
from fabric.contrib.console import confirm

from fab_shared import (_clone, _make_release, _nose_test, _upload_to_s3,
        TIME_NOW, _package_deploy)

env.unit = "django-comrade"
env.scm = "git@github.com:bueda/django-comrade" % env
env.root_dir = os.path.abspath(os.path.dirname(__file__))
env.allow_no_tag = True
env.upload_to_s3 = True
 
def deploy(release=None, skip_tests=None):
    _package_deploy(release, skip_tests)

@runs_once
def test(dir=None):
    if not dir:
        dir = env.root_dir
    with settings(root_dir=dir):
        local('python setup.py build', capture=False)
        return _nose_test()
