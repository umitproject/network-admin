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

import json
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from piston.handler import BaseHandler
from networks.models import Host
from events.models import Event
from webapi.views import api_error, api_ok, api_response
from piston.authentication import OAuthAuthentication

class HostHandler(BaseHandler):
    allowed_methods = ('GET', )
    
    def read(self, request, host_id=None):
        """Returns host details or hosts list"""
        
        if not host_id:
            # return hosts list
            hosts = Host.objects.all()
            if not hosts:
                return api_error(_('The hosts list is empty'))
            response = {
                'hosts': [{'id': host.pk, 'name': host.name} for host in hosts]
            }
            return api_response(response)
        
        try:
            # return host details
            host = Host.objects.get(pk=host_id)
        except Host.DoesNotExist:
            return api_error(_('Host does not exist'))
        
        response = {
            'host_id': host_id,
            'host_description': host.description,
            'ipv4': host.ipv4,
            'ipv6': host.ipv6
        }
        
        return api_response(response)
    
class EventHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    
    def create(self, request):
        """Report event"""
        e = request.POST
        
        ipv4 = e.get('source_host_ipv4')
        ipv6 = e.get('source_host_ipv6')
        
        if not (ipv4 or ipv6):
            return api_error(_('No IP address specified'))
        
        try:
            if ipv4 and ipv6:
                source_host = Host.objects.get(ipv4=ipv4, ipv6=ipv6)
            elif ipv4:
                source_host = Host.objects.get(ipv4=ipv4)
            elif ipv6:
                source_host = Host.objects.get(ipv6=ipv6)
        except Host.DoesNotExist:
            if ipv6:
                host_name = 'host %s, %s' % (ipv4, ipv6)
            else:
                host_name = 'host %s' % ipv4
            source_host = Host(name=host_name, ipv4=ipv4, ipv6=ipv6)
            source_host.save()
        except MultipleObjectsReturned:
            return api_error(_('There is more than one host with that IP'))
            
        try:
            event = Event(message=e['message'],
                      event_type=e['event_type'],
                      timestamp=e['timestamp'],
                      source_host=source_host,
                      monitoring_module = e['monitoring_module'],
                      monitoring_module_fields  = e['monitoring_module_fields'])
        except KeyError:
            return api_error(_('Report message is broken'))
        
        event.save()
        
        return api_ok(_('Event reported successfully'))
    
    def read(self, request, event_id=None):
        """Event details or events list"""
        
        if not event_id:
            # return events list
            events = Event.objects.all()
            if not events:
                return api_error(_('The events list is empty'))
            response = {
                'events': [{'id': event.pk, 'name': event.message} for event in events]
            }
            return api_response(response)
        
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return api_error(_('Event does not exist'))
        
        response = {
            'event_id': event_id,
            'message': event.message,
            'timestamp': str(event.timestamp),
            'event_type': event.event_type,
            'source_host_id': event.source_host.pk,
            'module_id': event.monitoring_module,
            'module_fields': event.monitoring_module_fields
        }
        
        return api_response(response)

