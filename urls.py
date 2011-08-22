from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
    (r'^api/', include('netadmin.webapi.urls')),
    (r'^network/', include('netadmin.networks.urls')),
    (r'^event/', include('netadmin.events.urls')),
    (r'^report/', include('netadmin.reportmeta.urls')),
    (r'^user/', include('netadmin.users.urls')),
    (r'^plugins/', include('netadmin.plugins.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^search/', 'netadmin.views.global_search', name='global_search'),
    
    url(r'login/', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}, name='login_page'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout'),

    url(r'^oauth/request_token/$','piston.authentication.oauth_request_token'),
    url(r'^oauth/authorize/$','piston.authentication.oauth_user_auth'),
    url(r'^oauth/access_token/$','netadmin.webapi.views.xauth_callback'),
    
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),
)
