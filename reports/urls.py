from django.conf.urls.defaults import *

urlpatterns = patterns('reports.views',
   url(r'^request/$', 'report_request'),
)
