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

from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from search.core import search

from events.forms import EventSearchForm, EventSearchSimpleForm
from events.models import Event, EventType
from events.utils import filter_user_events


@login_required
def events_list(request, adv_search=False):
    if adv_search:
        form_class = EventSearchForm
    else:
        form_class = EventSearchSimpleForm
        
    search_form = form_class(request.GET)
    
    events = None
    
    if search_form.is_valid():
        cleaned_data = search_form.cleaned_data
        
        search_phrase = cleaned_data.get('message')
        if search_phrase:
            events = search(Event, search_phrase)
        else:
            events = filter_user_events(request.user)
        
        date_after = cleaned_data.get('date_after')
        if date_after:
            events = events.filter(timestamp__gte=date_after)
            
        date_before = cleaned_data.get('date_before')
        if date_before:
            events = events.filter(timestamp__lte=date_before)
            
        event_type = cleaned_data.get('event_type')
        if event_type and event_type != '0':
            events = events.filter(event_type__pk=event_type)
    else:
        search_form = form_class()
        events = filter_user_events(request.user)
        
    events = events.order_by('timestamp')
    
    extra_context = {
        'events': events,
        'url': '/event/list/',
        'search_form': search_form,
        'adv_search': adv_search,
    }
    
    return direct_to_template(request, 'events/event_list.html',
                              extra_context=extra_context)

@login_required
def events_search(request):
    return events_list(request, adv_search=True)