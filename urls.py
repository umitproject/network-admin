from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    (r'^api/', include('webapi.urls')),
    #(r'^report/', include('reports.urls')),
    ('^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
    (r'^accounts/', include(admin.site.urls)),

    url(r'^oauth/request_token/$','piston.authentication.oauth_request_token'),
    url(r'^oauth/authorize/$','piston.authentication.oauth_user_auth'),
    url(r'^oauth/access_token/$','piston.authentication.oauth_access_token'),
)
