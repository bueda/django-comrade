from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

reverse_lazy = lazy(reverse, unicode)

urlpatterns = patterns('comrade.users.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^login/multipass/$', 'login',
            {'multipass': True, 'redirect_field_name': 'to'},
            name='multipass_login'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout', {'next_page':'/'}, name='logout'),
    url(r'^password/forgot/$', 'password_reset',
            {'post_reset_redirect':reverse_lazy('account:password_reset_done')},
            name='password_reset'),
    url(r'^password/forgot/done/$', 'password_reset_done',
            name='password_reset_done'),
    url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
            'password_reset_confirm',
            {'post_reset_redirect':
                reverse_lazy('account:password_reset_complete')},
            name='password_reset_confirm'),
    url(r'^password/reset/done/$', 'password_reset_complete',
            name='password_reset_complete'),
    url(r'^password/change/$', 'password_change',
            name='password_change'),
    url(r'^password/change/done', 'password_change_done',
            name='password_change'),
)
