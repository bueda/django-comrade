#!/usr/bin/env python
import os
from fabric.api import *
from fabric.contrib.console import confirm

from fab_shared import (_clone, _make_release, _nose_test,
        _conditional_upload_to_s3, TIME_NOW)

env.unit = "comrade"
env.scm = "git@github.com:bueda/django-comrade" % env
env.root_dir = os.path.abspath(os.path.dirname(__file__))
 
def deploy(release=None):
    """
    Deploy a specific commit, tag or HEAD to all servers and/or S3.
    """
    require('unit')

    env.scratch_path = '/tmp/%s-%s' % (env.unit, TIME_NOW)
    _clone(release)
    if test(env.scratch_path):
        abort("Unit tests did not pass")
    _make_release(release)
    require('pretty_release')
    require('archive')

    s3_filename = '%(unit)s.tar.gz' % env
    s3_file_source = '%(scratch_path)s/%(archive)s' % env
    _conditional_upload_to_s3(s3_file_source, s3_filename)

@runs_once
def test(dir=None):
    if not dir:
        dir = env.root_dir
    with settings(root_dir=dir):
        local('python setup.py build', capture=False)
        return _nose_test()
