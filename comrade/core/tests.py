from nose.tools import ok_
import unittest

from db.models import ComradeBaseModel

def check_direct_to_template(prefix, pattern):
    from django import test
    from django.core.urlresolvers import reverse
    client = test.Client()
    response = client.get(reverse(prefix + ':' + pattern.name))
    template_name = pattern.default_args['template']
    template_names = [t.name for t in test.testcases.to_list(response.template)]
    ok_(template_names)
    ok_(template_name in template_names,
        "Template '%s' was not a template used to render"
        " the response. Actual template(s) used: %s" %
            (template_name, u', '.join(template_names)))

class SimpleModel(ComradeBaseModel):
    def __unicode__(self):
        return u'This is a unicode string'

class TestBaseModel(unittest.TestCase):
    def setUp(self):
        super(TestBaseModel, self).setUp()
        self.obj = SimpleModel()

    def test_repr(self):
        ok_(isinstance(self.obj.__repr__(), str))

    def test_str(self):
        ok_(isinstance(self.obj.__str__(), str))

    def test_unicode(self):
        ok_(isinstance(self.obj.__unicode__(), unicode))
