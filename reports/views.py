from django.http import HttpResponse
from reports import RequestReport
from geraldo.generators import PDFGenerator

from inspect import ismethod

def report_request(request):
    data = []
    
    for name in dir(request):
        att = getattr(request, name)
        if name in ['GET', 'POST', 'COOKIES', 'META']:
            for k in att.keys():
                data.append({'type': name, 'name': k, 'value': str(att[k])})
            
    resp = HttpResponse(mimetype='application/pdf')
    
    report = RequestReport(queryset=data)
    report.generate_by(PDFGenerator, filename=resp)
    
    return resp