from django.conf.urls.defaults import *
from piston.resource import Resource
from webapi.handlers import *

host_handler = Resource(HostHandler)
event_handler = Resource(EventHandler)

urlpatterns = patterns('webapi.views',
   url(r'^host/(?P<host_id>\d+)/$', host_handler, name='host_detail'),
   url(r'^host/list/$', host_handler, name='host_list'),
   url(r'^event/report/$', event_handler),
   url(r'^event/(?P<event_id>\d+)/$', event_handler),
)
