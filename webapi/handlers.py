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
from webapi.views import api_error, api_ok

class HostHandler(BaseHandler):
    allowed_methods = ('GET', )
    
    def read(self, request, host_id=None):
        """Returns host details or hosts list"""
        if not host_id:
            # return hosts list
            hosts = Host.objects.all()
            if not hosts:
                return api_error('The hosts list is empty')
            response = {
                'hosts': [{'id': host.pk, 'name': host.name} for host in hosts]
            }
            return HttpResponse(json.dumps(response))
        
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
        
        return HttpResponse(json.dumps(response))
    
class EventHandler(BaseHandler):
    allowed_methods = ('POST', 'GET')
    
    def create(self, request):
        e = json.loads(request.POST['event'])
        event = Event(message=e['message'],
                      type=e['type'],
                      source_host_ipv4 = e['source_host_ipv4'],
                      source_host_ipv6 = e['source_host_ipv6'],
                      monitoring_module = e['monitoring_module'],
                      monitoring_module_fields  = e['monitoring_module_fields'])
        event.save()
        return api_ok('Event reported successfully')
    
    def read(self, request, event_id=None):
        """Returns report details"""
        if not event_id:
            return api_error(_('No event ID specified'))
        
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return api_error(_('Event does not exist'))
        
        response = {
            'event_id': event_id,
            'type': event.type,
            'source_host_ipv4': event.source_host_ipv4,
            'source_host_ipv6': event.source_host_ipv6,
            'module_id': event.monitoring_module,
            'module_fields': event.monitoring_module_fields
        }
        
        return HttpResponse(json.dumps(response))

