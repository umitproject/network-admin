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
from django.http import Http404
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from search.core import search

from netadmin.events.forms import EventSearchForm, EventSearchSimpleForm, \
    AlertForm
from netadmin.events.models import Event, EventType, Alert
from netadmin.events.utils import filter_user_events
from netadmin.permissions.utils import user_has_access, \
    get_object_or_forbidden


@login_required
def events_list(request, adv_search=False):
    if adv_search:
        form_class = EventSearchForm
    else:
        form_class = EventSearchSimpleForm
        
    search_form = form_class(request.GET)
    
    events = None
    
    if search_form.is_valid() and search_form.cleaned_data['message']:
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
            
        events = events.order_by('-timestamp')
        # filter events by user access
        events = [e for e in events if user_has_access(e, request.user)]
    else:
        search_form = form_class()
        events = filter_user_events(request.user).order_by('-timestamp')
    
    extra_context = {
        'events': events,
        'url': '/event/list/',
        'search_form': search_form,
        'adv_search': adv_search,
    }
    
    return direct_to_template(request, 'events/event_list.html',
                              extra_context=extra_context)
    
@login_required
def event_detail(request, object_id):
    event = Event.objects.get(pk=object_id)
    if not user_has_access(event.source_host, request.user):
        raise Http404()
    return object_detail(request, Event.objects.all(), object_id)

@login_required
def events_search(request):
    return events_list(request, adv_search=True)

@login_required
def event_check(request, object_id):
    event = get_object_or_404(Event, pk=object_id)
    if not event.checked:
        event.checked = True
        event.save()

@login_required
def alerts_edit(request, object_id=None):
    alert = Alert(user=request.user)
    form = AlertForm(instance=alert)
    
    if request.method == 'POST':
        form = AlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.save()
    
    if request.method == 'GET':
        if object_id:
            try:
                alert = Alert.objects.get(pk=object_id, user=request.user)
                alert.delete()
            except Alert.DoesNotExist:
                # Just ignore the request - someone probably mistyped URL
                # or refreshed the page after removing alert.
                pass
       
    extra_context = {
        'form': form,
        'alerts': Alert.objects.filter(user=request.user).order_by('-level')
    }
    return direct_to_template(request, 'events/alerts.html',
                              extra_context=extra_context)

@login_required    
def alerts_list(request, level_id):
    alerts = Alert.objects.filter(user=request.user, level=level_id)
    et_pks = [a.event_type.pk for a in alerts]
    user_events = filter_user_events(request.user)
    
    events = user_events.filter(event_type__pk__in=et_pks)
    events = events.order_by('-timestamp')
    
    extra_context = {
        'alerts': events,
        'level_name': alerts[0].get_level_display()
    }
    return direct_to_template(request, 'events/event_list.html',
                              extra_context=extra_context)