from django.conf.urls.defaults import *

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    (r'^api/', include('webapi.urls')),
    (r'^report/', include('reports.urls')),
    ('^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
)
