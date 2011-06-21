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

from django.utils.translation import ugettext as _

from networks.models import Host
from events.models import Event, EventType

class EventParseError(Exception):
    pass

def create_event_from_dict(event_dict):
    """
    Creates event from dictionary and saves it in the database. A dictionary
    has to have the following fields:
        * message,
        * timestamp,
        * source_host_ipv4 and/or source_host_ipv6,
        * event_type.
        
    There are also two optional fields:
        * monitoring_module,
        * monitoring_module_fields.
        
    For more info about meaning of those parameters, please look to the Event
    model class documentation.
    """
    
    message = event_dict.get('message')
    if not message:
        raise EventParseError, 'No message specified'
    
    timestamp = event_dict.get('timestamp')
    if not timestamp:
        raise EventParseError, 'No timestamp specified'
    
    monitoring_module = event_dict.get('monitoring_module', '')
    monitoring_module_fields = event_dict.get('monitoring_module_fields', '')
    
    ipv4 = event_dict.get('source_host_ipv4')
    ipv6 = event_dict.get('source_host_ipv6')
    
    if not (ipv4 or ipv6):
        raise EventParseError, 'No IP address specified'
    
    # Determine source host (according to the class' docstring)
    try:
        if ipv4 and ipv6:
            source_host = Host.objects.get(ipv4=ipv4, ipv6=ipv6)
        elif ipv4:
            source_host = Host.objects.get(ipv4=ipv4)
        elif ipv6:
            source_host = Host.objects.get(ipv6=ipv6)
    except Host.DoesNotExist:
        # create host if it does not exist
        if ipv6:
            host_name = 'host %s, %s' % (ipv4, ipv6)
        else:
            host_name = 'host %s' % ipv4
        source_host = Host(name=host_name, ipv4=ipv4, ipv6=ipv6)
        source_host.save()
    except MultipleObjectsReturned:
        raise EventParseError, 'There is more than one host with that IP'
        
    # Determine event type. If no type was specified, set default value
    event_type_name = event_dict.get('event_type')
    if not event_type_name:
        raise EventParseError, 'No event type specified'
    
    event_type, created = EventType.objects.get_or_create(name=event_type_name)

    event = Event(message=message,
                  event_type=event_type,
                  timestamp=timestamp,
                  source_host=source_host,
                  monitoring_module=monitoring_module,
                  monitoring_module_fields=monitoring_module_fields)
    event.save()
    
    return event