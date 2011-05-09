from django.conf.urls.defaults import *
from piston.resource import Resource
from webapi.handlers import ReportRequestHandler

report_request_handler = Resource(ReportRequestHandler)

urlpatterns = patterns('webapi.views',
   url(r'^request_report/$', report_request_handler),
)
