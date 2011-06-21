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
"""
This is the core module of the Network Administrator web API. Its main
purpose is to receive notifications and give access to hosts, networks
and reports data. It is based on RESTful web services and uses JSON to
serialize data.

The API has its private and public sections. The private section's task
is to receive notifications (events) from servers and save them into the
database. The public part is supposed to be the interface that will give
external applications access to informations about hosts, networks and
reports.

Our next goal for this API is to provide authentication with OAuth.
So far we are using system which simply sends user login and password
encoded with the base64 library.
"""

import simplejson as json

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from piston.handler import BaseHandler
from networks.models import Host, Network
from events.models import Event, EventType
from events.utils import create_event_from_dict, EventParseError

from webapi.views import api_error, api_ok, api_response

class HostHandler(BaseHandler):
    """
    Host handler is a part of the public API. It gives access to hosts data.
    """
    allowed_methods = ('GET', )
    
    def read(self, request, host_id=None):
        """
        Returns host details if host_id is specified, otherwise returns
        hosts list.
        
        Method: GET
        
        Request parameters:
            * host_id (optional) - if specified, host details are returned
            * get_events (optional) - if 'true' then return list of events
              for the host specified by host_id
            * order_by (optional) - if host_id is not specified, order
              hosts list according to this parameter; allowe values are:
                ** name - order by name
                ** last_event - order by occurance of last event
                
        Host details response:
            * host_id
            * host_name
            * host_description
            * ipv4 - IPv4 address of the host
            * ipv6 - IPv6 address of the host
            * events (optional) - list of events for the host
                ** id - event identifier
                ** message - event message
                
        Hosts list response:
            * hosts
                ** id - host identifier
                ** name - host name
        """
        
        if not host_id:
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
            host = Host.objects.get(pk=host_id, user=request.user)
        except Host.DoesNotExist:
            return api_error(_('Host does not exist'))
        
        response = {
            'host_id': host_id,
            'host_name': host.name,
            'host_description': host.description,
            'ipv4': host.ipv4,
            'ipv6': host.ipv6
        }
        
        get_hosts = request.GET.get('get_events', 'true')
        if get_hosts.lower() == 'true':
            response['events'] = [{'id': e.pk, 'message': e.message} for e in host.events]
        
        return api_response(response)
    
class NetworkHandler(BaseHandler):
    """
    This handler gives access to all informations about networks, like
    networks list or details of the specified network. This is a part
    of the public API.
    """
    allowed_methods = ('GET', )
    
    def read(self, request, network_id=None):
        """
        If the network_id is specified returns network details,
        otherwise returns networks list.
        
        Method: GET
        
        Request parematers:
            * network_id (optional) - network which details we want
            * get_hosts (optional) - if 'true' and network_id is
              specified, then list of hosts in the network is returned
            * order_by (optional) - if network_id is not specified
              then networks list will be sorted according to this
              parameter; the allowed values are:
                ** name - order by name
                ** last_event - order by occurance of last event
        
        Network details response:
            * network_id
            * network_name - name of the network
            * network_description - description of the network
            * hosts (optional)
                ** id - host identifier
                ** name - host name
            
        Networks list reponse:
            * networks
                ** id - network identifier
                ** name - network name
        """ 
        
        if not network_id:
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
    """
    Event handler is responsible for receiving notifications (events)
    and saving them to the Network Administrator database. Its second
    task is to return events list or details of event.
    
    Every event has its source host which is the host from where it
    comes. In the notification the source host is identified by pair
    of IPv4 and IPv6 addresses, where the second one is optional so far.
    So to relate the upcoming event with the corresponding host in
    database we have to search for the host which has the same
    addresses like the source host in the notification. 
    """
    allowed_methods = ('POST', 'GET')
    
    def create(self, request):
        """
        Receives one or more notifications and saves them to the database.
        This method is a part of private API.
        
        Method: POST
        URL: /api/event/report/
        
        Case 1: Reporting single event (notification)
        ---------------------------------------------
        
        Request parameters:
            * message - short message identifying the event
            * timestamp - when the event occurred
            * event_type - type of the event which should also describe
              its importance
            * source_host_ipv4, source_host_ipv6 - IPv4 and IPv6
              addresses of the source host
            * monitoring_module (optional) - monitoring module identifier
            * monitoring_module_fields (optional) - serialized monitoring
              module parameters
              
        Response:
            * status - **ok** or **error**
            * message - details of the result
            
        Case 2: Reporting multiple events at once
        -----------------------------------------
        
        Request parameters:
            * events - list of events serialized with JSON
            
        Response:
            * status - **ok** or **error**
            * message - details of the result
        
        """
        
        if request.POST.get('events'):
            try:
                events = json.loads(request.POST.get('events', ''))
            except ValueError:
                return api_error(_('No events could be read'))
            
            for event in events:
                try:
                    create_event_from_dict(event)
                except EventParseError, e:
                    api_error(_(e))
            
            return api_ok(_('Events reported successfully'))
        
        event = request.POST
        try:
            create_event_from_dict(event)
        except EventParseError, e:
            api_error(_(e))
        
        return api_ok(_('Event reported successfully'))
    
    def read(self, request, event_id=None):
        """
        If the event_id parameter is specified, returns event details,
        otherwise returns events list. This falls under the public API.
        
        Method: GET
        
        Response for events list:
            * events - list of events
                ** id - event identifier
                ** message - event message
                
        Response for event details:
            * event_id
            * message - event message
            * timestamp - event timestamp
            * event_type - type of event 
            * source_host_id - identifier of source host
            * module_id - identifier of monitoring module
            * module_fields - fields defined by monitoring module
        """
        
        if not event_id:
            events = Event.objects.all()
            if not events:
                return api_error(_('The events list is empty'))
            
            events = filter(lambda event: event.user == request.user, events)
            
            response = {
                'events': [{'id': event.pk, 'message': event.message} for event in events]
            }
            return api_response(response)
        
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return api_error(_('Event does not exist'))
        
        if event.user != request.user:
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
