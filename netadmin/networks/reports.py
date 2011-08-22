#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Piotrek Wasilewski <wasilewski.piotrek@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../../reportlab.zip'))

from reportlab.lib.units import cm
from geraldo import Report, SubReport, ReportBand, ObjectValue, \
    SystemField, Label, BAND_WIDTH
from reportlab.lib.enums import TA_CENTER

class HostReport(Report):
    title = 'Host report'
    margin_left = margin_top = margin_right = margin_bottom = 2*cm
    print_if_empty = True
    
    def __init__(self, title, *args, **kwargs):
        self.title = title
        super(HostReport, self).__init__(*args, **kwargs)
        
    class band_page_header(ReportBand):
        height = 1.3*cm
        elements = [
                SystemField(expression="%(report_title)s",
                    top=0*cm, left=0, width=BAND_WIDTH,
                    style={'fontName': 'Helvetica-Bold',
                           'fontSize': 14, 'alignment': TA_CENTER}),
                SystemField(expression=u"Generated on %(now:%Y, %b %d)s at %(now:%H:%M)s",
                    top=0.1*cm, left=0*cm),
                ]
        borders = {'bottom': True}
    
    class band_header(ReportBand):
        height = 0.6*cm
        elements=[
                Label(text='Timestamp', top=.5*cm, left=0*cm, width=3*cm,
                    style={'fontName': 'Helvetica-Bold'}),
                Label(text='Message', top=.5*cm, left=3*cm, width=8*cm,
                    style={'fontName': 'Helvetica-Bold'}),
                Label(text='Event type', top=.5*cm, left=12*cm, width=1.5*cm,
                    style={'fontName': 'Helvetica-Bold'}),
            ]
        borders = {'bottom': True}
            
    class band_detail(ReportBand):
        height=2*cm
        elements=[
            ObjectValue(attribute_name='timestamp', top=0, left=0*cm, width=3*cm,
                get_value=lambda instance: instance.timestamp.strftime('%m-%d-%Y %H:%M')),
            ObjectValue(attribute_name='message', top=0, left=3*cm, width=11*cm),
            ObjectValue(attribute_name='event_type', top=0, left=14.5*cm),
        ]
        borders = {'bottom': True}
        
class NetworkReport(Report):
    title = 'Network report'
    margin_left = margin_top = margin_right = margin_bottom = 2*cm
    print_if_empty = True
    
    def __init__(self, title, *args, **kwargs):
        self.title = title
        super(NetworkReport, self).__init__(*args, **kwargs)
        
    class band_page_header(ReportBand):
        height = 1.3*cm
        elements = [
                SystemField(expression="%(report_title)s",
                    top=0*cm, left=0, width=BAND_WIDTH,
                    style={'fontName': 'Helvetica-Bold',
                           'fontSize': 14, 'alignment': TA_CENTER}),
                SystemField(expression=u"Generated on %(now:%Y, %b %d)s at %(now:%H:%M)s",
                    top=0.1*cm, left=0*cm),
                ]
        borders = {'bottom': True}
    
    class band_header(ReportBand):
        height = 0.6*cm
        elements=[
                Label(text='Timestamp', top=.5*cm, left=0*cm, width=3*cm,
                    style={'fontName': 'Helvetica-Bold'}),
                Label(text='Message', top=.5*cm, left=3*cm, width=8*cm,
                    style={'fontName': 'Helvetica-Bold'}),
                Label(text='Event type', top=.5*cm, left=12*cm, width=1.5*cm,
                    style={'fontName': 'Helvetica-Bold'}),
                Label(text='Source host', top=.5*cm, left=14*cm,
                    style={'fontName': 'Helvetica-Bold'}),
            ]
        borders = {'bottom': True}
            
    class band_detail(ReportBand):
        height=2.5*cm
        elements=[
            ObjectValue(attribute_name='timestamp', top=0, left=0*cm, width=3*cm,
                get_value=lambda instance: instance.timestamp.strftime('%m-%d-%Y %H:%M')),
            ObjectValue(attribute_name='message', top=0, left=3*cm, width=8*cm),
            ObjectValue(attribute_name='event_type', top=0, left=12*cm, width=1.5*cm),
            ObjectValue(attribute_name='source_host', top=0, left=14*cm,
                get_value=lambda instance: instance.source_host.name),
        ]
        borders = {'bottom': True}
    