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

from datetime import timedelta

from events.models import Event, EventType
from networks.models import Host, Network


def get_events(time_from=None, time_to=None, source_hosts=[]):
    """
    get_events(...) -> QuerySet
    
    Returns events, optionally filtering them by timestamp
    or source hosts.
    """
    events = Event.objects.all()
    if source_hosts:
        pks = [host.pk for host in source_hosts]
        events = events.filter(source_host__pk__in=pks)
    if time_from:
        events = events.filter(timestamp__gte=time_from)
    if time_to:
        events = events.filter(timestamp__lt=time_to)
    return events

def get_eventtypes(user=None, alert=0):
    """
    get_eventtypes(...) -> QuerySet
    
    Returns events' types, filtering them by user and/or alert
    level if specified.
    """
    eventtypes = EventType.objects.all()
    if user:
        eventtypes = eventtypes.filter(user=user)
    if alert:
        eventtypes = eventtypes.filter(alert_level__gte=alert)
    return eventtypes

def get_alerts(user=None):
    ets = [et.pk for et in get_eventtypes(user, 1)]
    return Event.objects.filter(event_type__pk__in=ets, checked=False)

def _get_network_objects(subclass, user=None):
    objects = subclass.objects.all()
    if user:
        objects = objects.filter(user=user)
    return objects

def get_host(id):
    return Host.objects.get(pk=id)

def get_hosts(user=None):
    return _get_network_objects(Host, user)

def get_networks(user=None):
    return _get_network_objects(Network, user)
