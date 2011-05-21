from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication, NoAuthentication
from webapi.handlers import *

auth = HttpBasicAuthentication()
ad = { 'authentication': auth }

host_handler = Resource(HostHandler, **ad)
event_handler = Resource(EventHandler, **ad)

urlpatterns = patterns('webapi.views',
   url(r'^host/(?P<host_id>\d+)/$', host_handler, name='host_detail'),
   url(r'^host/list/$', host_handler, name='host_list'),
   url(r'^event/report/$', event_handler, name="report_event"),
   url(r'^event/(?P<event_id>\d+)/$', event_handler),
)
