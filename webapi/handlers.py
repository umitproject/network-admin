from django.http import HttpResponse

from piston.handler import BaseHandler
from reports.reports import RequestReport

from geraldo.generators import TextGenerator

class ReportRequestHandler(BaseHandler):
   allowed_methods = ('GET',)
   
   def read(self, request):
       
       data = []
    
       for name in dir(request):
           att = getattr(request, name)
           if name in ['GET', 'POST', 'COOKIES', 'META']:
               for k in att.keys():
                   data.append({'type': name, 'name': k, 'value': str(att[k])})
       
       report = RequestReport(data)
       resp = report.generate_by(TextGenerator)
       
       return resp
