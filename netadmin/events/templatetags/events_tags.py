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

import datetime

from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext as _

from netadmin.events.models import Event, EventType, ALERT_LEVELS
from netadmin.events.utils import filter_user_events


register = template.Library()


@register.inclusion_tag('events/alerts_counter.html')
def alerts_counter(user_id):
    user_alerts = EventType.objects.filter(user__pk=user_id,
                                           alert_level__gte=1)
    
    alert_levels = {}
    for alert in user_alerts:
        level = alert.alert_level
        events_count = alert.pending_events().count()
        if level in alert_levels:
            alert_levels[level] += events_count
        else:
            alert_levels[level] = events_count
    
    alert_levels_list = []
    for id, name in ALERT_LEVELS:
        if id in alert_levels:
            count = alert_levels[id]
            alert_levels_list.append((id, name, count))
    return {'alert_levels': alert_levels_list}

@register.inclusion_tag('events/events_list_tag.html')
def events_list(request, events, title=None, page=None):
    paginator = Paginator(list(events), 20)
    
    page = page or request.GET.get('page', 1)
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)
    
    context = {
        'events': events,
        'title': title,
        'request': request
    }
    return context

@register.inclusion_tag('events/events_list_tag.html')
def similar_events(request, event):
    event_type = event.event_type
    events = filter_user_events(event.user).filter(event_type=event_type)
    events = events.exclude(pk=event.pk)
    return events_list(request, events[:10], "Similar events")
