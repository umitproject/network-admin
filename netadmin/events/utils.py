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

try:
    import simplejson as json
except ImportError:
    import json

import datetime

from django.utils.translation import ugettext as _

from netadmin.permissions.utils import filter_user_objects
from netadmin.networks.models import Host
from netadmin.events.models import Event, EventType


class EventParseError(Exception):
    pass

def filter_user_events(user):
    """Returns events accessible to specified user.
    """
    hosts = filter_user_objects(user, Host)
    pks = [host.pk for host in hosts]
    return Event.objects.filter(source_host__pk__in=pks)

def get_event_data(request, event_dict):
    """
    Creates dictionary with parameters for Event's __init__ method. If needed
    function also creates host and event type and saves them. If function
    cannot find obligatory fields in event_dict, it raises EventParseError
    exception.
    """
    required_fields = ['timestamp', 'protocol', 'fields_class', 'event_type',
                       'description', 'short_description']
    base_fields = required_fields + ['is_report', 'hostname',
                                     'source_host_ipv6', 'source_host_ipv4']
    
    # make sure that event_dict contains all fields we need
    # (also make sure that these fields aren't empty)
    for field_name in required_fields:
        if field_name not in event_dict:
            raise EventParseError("Following field is not specified: %s" \
                                    % field_name)
        if not event_dict[field_name]:
            raise EventParseError("Following field must not be empty: %s" \
                                    % field_name)
        
    message = event_dict['description']
    short_message = event_dict['short_description']
    timestamp = event_dict['timestamp']
    protocol = event_dict['protocol']
    event_type_name = event_dict['event_type']
    fields_class = event_dict['fields_class']
    
    ipv4 = event_dict.get('source_host_ipv4')
    ipv6 = event_dict.get('source_host_ipv6')
    hostname = event_dict.get('hostname')
    
    try:
        # TODO
        # filter by user=request.user!!!
        if hostname:
            source_host = Host.objects.get(name=hostname, user=request.user)
        else:
            if ipv4 and ipv6:
                source_host = Host.objects.get(ipv4=ipv4, ipv6=ipv6,
                                               user=request.user)
            elif ipv4:
                source_host = Host.objects.get(ipv4=ipv4, user=request.user)
            elif ipv6:
                source_host = Host.objects.get(ipv6=ipv6, user=request.user)
            else:
                source_host = None
    except Host.DoesNotExist:
        source_host = Host(name=hostname, ipv4=ipv4, ipv6=ipv6,
                           user=request.user)
        source_host.save()
    
    try:
        event_type = EventType.objects.get(name=event_type_name,
                                           user=request.user)
    except EventType.DoesNotExist:
        event_type = EventType(name=event_type_name, user=request.user)
        event_type.save()
        
    fields_data_dict = {}
    for field in event_dict:
        if field not in base_fields:
            fields_data_dict[field] = event_dict[field]
    fields_data = json.dumps(fields_data_dict)
        
    event_data = {
        'message': message,
        'short_message': short_message,
        'timestamp': datetime.datetime.fromtimestamp(float(timestamp)),
        'protocol': protocol,
        'fields_class': fields_class,
        'fields_data': fields_data,
        'source_host': source_host,
        'event_type': event_type
    }
    
    return event_data
    