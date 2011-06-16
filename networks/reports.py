import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../reportlab.zip'))

from reportlab.lib.units import cm
from geraldo import Report, SubReport, ReportBand, ObjectValue, SystemField, Label, BAND_WIDTH

class HostReport(Report):
    title = 'Host report'
    margin_left = margin_top = margin_right = margin_bottom = 2*cm
    
    class band_detail(ReportBand):
        height = 8*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 14}),
            SystemField(expression='%(now:%m-%d-%Y)s', top=1*cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica', 'fontSize': 12}, borders={'bottom': True}, height=-0.7*cm),
            Label(text="Name", top=2*cm, left=0, style={'fontName': 'Helvetica-Bold'}),
            Label(text="IPv4 address", top=3*cm, left=0, style={'fontName': 'Helvetica-Bold'}),
            Label(text="IPv6 address", top=4*cm, left=0, style={'fontName': 'Helvetica-Bold'}),
            Label(text="Description", top=5*cm, left=0, style={'fontName': 'Helvetica-Bold'}),
            ObjectValue(attribute_name='name', top=2*cm, left=3*cm, width=12*cm),
            ObjectValue(attribute_name='ipv4', top=3*cm, left=3*cm, width=12*cm),
            ObjectValue(attribute_name='ipv6', top=4*cm, left=3*cm, width=12*cm),
            ObjectValue(attribute_name='description', top=5*cm, left=3*cm, width=12*cm),
        ]
        borders = {'bottom': True}
        
    subreports = [
        SubReport(
            queryset_string = '%(object)s.events',
            
            band_header = ReportBand(
                height = 0.6*cm,
                elements=[
                    Label(text='Timestamp', top=0, left=0*cm, style={'fontName': 'Helvetica-Bold'}),
                    Label(text='Message', top=0, left=5*cm, style={'fontName': 'Helvetica-Bold'}),
                    Label(text='Event type', top=0, left=14*cm, style={'fontName': 'Helvetica-Bold'}),
                ],
                borders = {'bottom': True}
            ),
            
            detail_band = ReportBand(
                height=0.5*cm,
                elements=[
                    ObjectValue(attribute_name='timestamp', top=0, left=0*cm,
                                get_value=lambda instance: instance.timestamp.strftime('%m-%d-%Y %H:%M')),
                    ObjectValue(attribute_name='message', top=0, left=5*cm),
                    ObjectValue(attribute_name='event_type', top=0, left=14*cm),
                ]
            ),
                  
        ),
    ]
        
class NetworkReport(Report):
    title = 'Network report'
    margin_left = margin_top = margin_right = margin_bottom = 2*cm
    
    class band_detail(ReportBand):
        height = 6*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 14}),
            SystemField(expression='%(now:%m-%d-%Y)s', top=1*cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica', 'fontSize': 12}, borders={'bottom': True}, height=-0.7*cm),
            Label(text="Name", top=2*cm, left=0, style={'fontName': 'Helvetica-Bold'}),
            Label(text="Description", top=3*cm, left=0, style={'fontName': 'Helvetica-Bold'}),
            ObjectValue(attribute_name='name', top=2*cm, left=3*cm, width=12*cm),
            ObjectValue(attribute_name='description', top=3*cm, left=3*cm, width=12*cm),
        ]
        borders = {'bottom': True}
        
    subreports = [
        SubReport(
            queryset_string = '%(object)s.events',
            
            band_header = ReportBand(
                height = 0.6*cm,
                elements=[
                    Label(text='Timestamp', top=0, left=0*cm, style={'fontName': 'Helvetica-Bold'}),
                    Label(text='Message', top=0, left=5*cm, style={'fontName': 'Helvetica-Bold'}),
                    Label(text='Event type', top=0, left=10*cm, style={'fontName': 'Helvetica-Bold'}),
                    Label(text='Source host', top=0, left=14*cm, style={'fontName': 'Helvetica-Bold'}),
                ],
                borders = {'bottom': True}
            ),
            
            detail_band = ReportBand(
                height=0.5*cm,
                elements=[
                    ObjectValue(attribute_name='timestamp', top=0, left=0*cm,
                                get_value=lambda instance: instance.timestamp.strftime('%m-%d-%Y %H:%M')),
                    ObjectValue(attribute_name='message', top=0, left=5*cm),
                    ObjectValue(attribute_name='event_type', top=0, left=10*cm, width=4*cm),
                    ObjectValue(attribute_name='source_host', top=0, left=14*cm, width=4*cm,
                                get_value=lambda instance: instance.source_host.name),
                ]
            ),
                  
        ),
    ]