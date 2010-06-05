from django.conf.urls.defaults import *

urlpatterns = patterns('django.contrib.auth.views',
    url(r'^login/', 'login', name='login'),
    url(r'^logout/', 'logout', {'next_page':'/'}, name='logout'),
    url(r'^password/forgot/$', 'password_reset',
            # LH #269 - ideally this wouldn't be hard coded
            {'post_reset_redirect':'/accounts/password/forgot/done/'},
            name='password_reset'),
    url(r'^password/forgot/done/$', 'password_reset_done',
            name='password_reset_done'),
    url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
            'password_reset_confirm',
            # LH #269
            {'post_reset_redirect':'/accounts/password/reset/done/'},
            name='password_reset_confirm'),
    url(r'^password/reset/done/$', 'password_reset_complete',
            name='password_reset_complete'),
    url(r'^password/change/', 'password_change',
            name='password_change'),
    url(r'^password/change/done', 'password_change_done',
            name='password_change'),
)
