from nose.tools import ok_, eq_
import unittest

import models

class SimpleModel(models.ComradeBaseModel):
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

