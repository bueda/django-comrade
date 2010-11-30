from django import test
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.cache import cache

from nose.tools import eq_, ok_
import json
import mockito

class BaseTest(test.TestCase):
    fixtures = ['dev']

    def setUp(self):
        super(BaseTest, self).setUp()
        self.user = User.objects.get(username='test')
        self.login()

    def tearDown(self):
        super(BaseTest, self).tearDown()
        mockito.unstub()
        cache.clear()

    def login(self):
        return self.client.login(username='test', password='test')

    def _test_unauthenticated(self, method, url, allowed=False):
        self.client.logout()
        response = method(url)
        if not allowed:
            self.assertRedirects(response, reverse('account:login') +
                    '?' + REDIRECT_FIELD_NAME + '=' + url)
        else:
            eq_(response.status_code, 200)

    def _test_method_not_allowed(self, method, url):
        response = method(url)
        eq_(response.status_code, 405)

    def assertJsonContains(self, response, key, value, status_code=200,
            msg_prefix=''):
        if msg_prefix:
            msg_prefix += ": "

        self.assertEqual(response.status_code, status_code,
            msg_prefix + "Couldn't retrieve page: Response code was %d"
            " (expected %d)" % (response.status_code, status_code))
        json = json.loads(response.content)
        assert key in json
        eq_(json[key], value)


class BaseModelTest(BaseTest):
    def check_unicode(self):
        ok_(isinstance(self.instance.__unicode__(), unicode))
