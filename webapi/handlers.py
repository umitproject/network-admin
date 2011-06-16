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

import simplejson as json
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from piston.handler import BaseHandler
from networks.models import Host, Network
from events.models import Event, EventType
from webapi.views import api_error, api_ok, api_response

class HostHandler(BaseHandler):
    allowed_methods = ('GET', )
    
    def read(self, request, host_id=None):
        """Returns host details or hosts list"""
        
        if not host_id:
            # return hosts list
            hosts = Host.objects.filter(user=request.user)
            if not hosts:
                return api_error(_('The hosts list is empty'))
            
            order_by = request.GET.get('order_by', 'name')
            if order_by == 'name':
                hosts = hosts.order_by('name')
            elif order_by == 'last_event':
                hosts = sorted(hosts, key=lambda host: host.last_event)
            
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
            'host_name': host.name,
            'host_description': host.description,
            'ipv4': host.ipv4,
            'ipv6': host.ipv6
        }
        
        return api_response(response)
    
class NetworkHandler(BaseHandler):
    allowed_methods = ('GET', )
    
    def read(self, request, network_id=None):
        
        if not network_id:
            # return networks list
            networks = Network.objects.filter(user=request.user)
            if not networks:
                return api_error(_('The networks list is empty'))
            
            order_by = request.GET.get('order_by', 'name')
            if order_by == 'name':
                networks = networks.order_by('name')
            elif order_by == 'last_event':
                networks = sorted(networks, key=lambda net: net.last_event)
            
            response = {
                'networks': [{'id': net.pk, 'name': net.name} for net in networks]
            }
            return api_response(response)
        
        network = Network.objects.get(pk=network_id, user=request.user)
        
        response = {
            'network_id': network.pk,
            'network_name': network.name,
            'network_descrption': network.description
        }
        
        get_hosts = request.GET.get('get_hosts', 'true')
        if get_hosts.lower() == 'true':
            response['hosts'] = [{'id': h.pk, 'name': h.name} for h in network.hosts]
            
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
        
        # Determine source host
        try:
            if ipv4 and ipv6:
                source_host = Host.objects.get(ipv4=ipv4, ipv6=ipv6)
            elif ipv4:
                source_host = Host.objects.get(ipv4=ipv4)
            elif ipv6:
                source_host = Host.objects.get(ipv6=ipv6)
        except Host.DoesNotExist:
            # create host if it does not exist in database
            if ipv6:
                host_name = 'host %s, %s' % (ipv4, ipv6)
            else:
                host_name = 'host %s' % ipv4
            source_host = Host(name=host_name, ipv4=ipv4, ipv6=ipv6)
            source_host.save()
        except MultipleObjectsReturned:
            return api_error(_('There is more than one host with that IP'))
            
        # Determine event type. If no type was specified, set default value
        event_type_name = e.get('event_type')
        if not event_type_name:
            return api_error(_('No event type specified'))
        
        event_type, created = EventType.objects.get_or_create(name=event_type_name)
            
        try:
            event = Event(message=e['message'],
                      event_type=event_type,
                      timestamp=e['timestamp'],
                      source_host=source_host,
                      monitoring_module = e['monitoring_module'],
                      monitoring_module_fields  = e['monitoring_module_fields'])
        except KeyError, field:
            return api_error(_("The '%(field)s' field is missing") % {'field': field})
        
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
                'events': [{'id': event.pk, 'message': event.message} for event in events]
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
            'event_type': event.event_type.name,
            'source_host_id': event.source_host.pk,
            'module_id': event.monitoring_module,
            'module_fields': event.monitoring_module_fields
        }
        
        return api_response(response)
