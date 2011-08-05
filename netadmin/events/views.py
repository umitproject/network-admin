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
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponse
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from search.core import search

from netadmin.events.forms import EventSearchForm, EventSearchSimpleForm, \
    EventTypeFormset
from netadmin.events.models import Event, EventType, EventNotification, \
    ALERT_LEVELS
from netadmin.events.utils import filter_user_events
from netadmin.notifier.utils import NotifierQueue, NotifierEmptyQueue
from netadmin.permissions.utils import user_has_access, \
    get_object_or_forbidden


@login_required
def events_list(request, events=None, alerts=None, search_form=None,
                events_header=_("All events"), 
                template_name='events/event_list.html', extra_context=None):
    if not events and not isinstance(events, QuerySet):
        events = filter_user_events(request.user)
        
    if not search_form:
        search_form = EventSearchSimpleForm()
    
    events = events.order_by('-timestamp')
        
    context = {
        'alerts': alerts,
        'events': events,
        'events_header': events_header,
        'search_form': search_form
    }
    
    if extra_context:
        context.update(extra_context)
    
    return direct_to_template(request, template_name,
                              extra_context=context)

@login_required
def events_alerts(request, alert_level_id=None, alert_level_slug=None):
    
    levels = reversed(ALERT_LEVELS)
    
    if alert_level_id:
        for id, name in levels:
            if id == int(alert_level_id):
                levels = [(id, name)]
                break
    elif alert_level_slug:
        for id, name in levels:
            if name.lower() == alert_level_slug:
                levels = [(id, name)]
                break
    
    alerts = []
    for lvl_id, lvl_name in levels:
        # we ignore zero-level alert
        if not lvl_id:
            break
        types = EventType.objects.filter(user=request.user, alert_level=lvl_id)
        if types:
            types_pks = [t.pk for t in types]
            events = Event.objects.filter(event_type__pk__in=types_pks)
            events = events.order_by('-timestamp')
            alert = (events, lvl_name)
            alerts.append(alert)
    
    try:
        no_alert_type = EventType.objects.get(alert_level=0)
        events = Event.objects.filter(event_type=no_alert_type)
    except EventType.DoesNotExist:
        events = Event.objects.none()
    
    return events_list(request, events, alerts,
                       events_header=_("Other events"))

@login_required
def events_date(request, year, month=None, day=None):
    year, month, day = int(year), int(month), int(day)
    date_begin = datetime.datetime(year, month, day)
    date_end = datetime.datetime(year, month, day+1)
    
    events = filter_user_events(request.user)
    events = events.filter(timestamp__gte=date_begin, timestamp__lte=date_end)
    
    header = _("Events on %s") % date_begin.date()
    
    return events_list(request, events, events_header=header)

@login_required
def events_search(request):
    search_form = EventSearchForm(request.user, request.GET)
    
    events = None
    
    if search_form.is_valid() and search_form.cleaned_data['message']:
        cleaned_data = search_form.cleaned_data
        
        search_phrase = cleaned_data.get('message')
        events = search(Event, search_phrase)
        
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
        search_form = EventSearchForm(request.user)
    
    extra_context = {
        'adv_search': True,
    }
    
    return events_list(request, events, search_form=search_form,
                       template_name='events/event_search.html',
                       extra_context=extra_context)
    
@login_required
def events_stats(request):
    eventtypes = EventType.objects.filter(user=request.user)
    
    eventtypes_chart = EventTypesChart(7, eventtypes)
    eventtypescount_chart = EventTypesCountChart(eventtypes)
    
    context = {
        'eventtypes_chart': eventtypes_chart,
        'eventtypescount_chart': eventtypescount_chart
    }
    
    return direct_to_template(request, "events/event_stats.html",
                              extra_context=context)

@login_required
def event_detail(request, object_id=None, message_slug=None):
    if object_id:
        event = Event.objects.get(pk=object_id)
    elif message_slug:
        event = Event.objects.get(message_slug=message_slug)
    else:
        return events_list(request)
    if not user_has_access(event.source_host, request.user):
        raise Http404()
    return object_detail(request, Event.objects.all(),
                         slug=message_slug, slug_field='message_slug')

@login_required
def event_check(request, object_id):
    event = get_object_or_404(Event, pk=object_id)
    if not event.checked:
        event.checked = True
        event.save()
        
@login_required
def eventtype_detail(request, event_type_id=None, event_type_slug=None):
    if event_type_id:
        et = EventType.objects.get(pk=event_type_id)
    elif event_type_slug:
        et = EventType.objects.get(name_slug=event_type_slug)
    else:
        return events_list(request)
    events = Event.objects.filter(event_type__pk=et.pk)
    header = _("%s events") % et.name
    return events_list(request, events, events_header=header)

@login_required
def eventtype_edit(request):
    if request.method == 'POST':
        eventtype_formset = EventTypeFormset(request.POST)
        if eventtype_formset.is_valid():
            eventtype_formset.save()
    
    event_types = EventType.objects.filter(user=request.user).order_by('name')
    eventtype_formset = EventTypeFormset(queryset=event_types)
    
    extra_context = {
        'eventtype_formset': eventtype_formset
    }
    return direct_to_template(request, 'events/eventtype_edit.html',
                              extra_context=extra_context)
    
@login_required
def events_notify(request):
    notifier = NotifierQueue(EventNotification)
    try:
        log = notifier.send_emails(_("You have new alert(s) "
                                     "in Network Administrator"),
                                   clear_queue=False)
    except NotifierEmptyQueue:
        log = []
    if log:
        response = "<p>Emails sent:</p>%s" % '<br />'.join(log)
    else:
        response = "<p>No emails to send</p>"
    return HttpResponse(response)