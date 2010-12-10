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
        self.login()

    def tearDown(self):
        super(BaseTest, self).tearDown()
        mockito.unstub()
        cache.clear()

    def login(self, password=None):
        return self.client.login(username=(
                    getattr(self, 'user', None) and self.user.username) or 'test',
                password=password or 'test')

    def _test_unauthenticated(self, method, url, next_url=None, allowed=False):
        self.client.logout()
        self._test_unauthorized(method, url, next_url, allowed)

    def _test_unauthorized(self, method, url, next_url=None, allowed=False):
        response = method(url)
        if not allowed:
            self.assertRedirects(response,
                    (next_url or reverse('account:login')) +
                    '?' + REDIRECT_FIELD_NAME + '=' + url)
        else:
            eq_(response.status_code, 200)

    def _test_method_not_allowed(self, method, url):
        response = method(url)
        eq_(response.status_code, 405)

    def assertJsonContains(self, response, key, value=None, status_code=200,
            msg_prefix=''):
        if msg_prefix:
            msg_prefix += ": "

        self.assertEqual(response.status_code, status_code,
            msg_prefix + "Couldn't retrieve page: Response code was %d"
            " (expected %d)" % (response.status_code, status_code))
        data = json.loads(response.content)
        ok_(key in data, msg_prefix + "Couldn't find key '%s' in JSON:\n %s" %
                (key, data))
        if value is not None:
            eq_(data[key], value)


class BaseModelTest(BaseTest):
    def setUp(self, instance=None):
        super(BaseModelTest, self).setUp()
        self.instance = instance

    def test_unicode(self):
        if self.instance:
            ok_(isinstance(self.instance.__unicode__(), unicode))
