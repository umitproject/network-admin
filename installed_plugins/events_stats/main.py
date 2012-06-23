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

from netadmin.plugins import Plugin, Widget
from netadmin.shortcuts import get_user_events, get_hosts, get_host, \
    get_eventtypes, get_events

class EventsStatsWidget(Widget):
    name = _("Latest events")
    description = _("Shows information about latest events")
    template_name = "latest_events.html"
    username = []
		
    def get_title(self, widget):
		title = self.get_option('latest_events_widget_title', widget)
		return title
    
    def options(self, widget):
        hosts = get_hosts(self.user)
        hosts_choices = [(-1, '-- all --')] + \
            [(h.pk, h.name) for h in hosts]
            
        alert_levels = [(-1, _('-- any --')), (1, _('Low')),
                        (2, _('Medium')), (3, _('High'))]
        return {
            'latest_events_widget_number_of_events': {
                'label': _("Number of events to show"),
                'choices': [(i, i) for i in xrange(1, 16)],
                'default': 5
            },
            'latest_events_widget_title': {
                'label': _("Title of the widget"),
                'default': _("Latest events"),
                'return_func': lambda value: str(value)
            },
            'latest_events_widget_host': {
                'label': _("Events from host"),
                'choices': hosts_choices,
                'default': -1,
                'return_func': lambda value: None if value == '-1' else get_host(value)
            },
            'latest_events_widget_alert_level': {
                'label': _("Alert level"),
                'choices': alert_levels,
                'default': -1,
                'return_func': lambda value: int(value)
            },
            'latest_events_widget_checked': {
                'label': _("Hide events marked as checked"),
                'choices': [(0, 'No'), (1, 'Yes')],
                'default': 0,
                'return_func': lambda value: True if value == '1' else False
            }
        }
        
    def context(self, widget):
        host = self.get_option('latest_events_widget_host', widget)
        alert_level = self.get_option('latest_events_widget_alert_level', widget)
        
        if host:
            if alert_level > 0:
                event_types = get_eventtypes(self.user, alert=alert_level)
                events = get_events(source_hosts=[host],
                                    event_types=event_types)
            else:
                events = host.events()
        else:
            if alert_level > 0:
                event_types = get_eventtypes(self.user, alert=alert_level)
                events = get_events(event_types=event_types)
            else:
                events = get_user_events(self.user)
        
        checked = self.get_option('latest_events_widget_checked', widget)
        if checked:
            events = events.filter(checked=False)
        
        limit = self.get_option('latest_events_widget_number_of_events', widget)
        return {
            'events': events.order_by('-timestamp')[:limit]
        }

class EventsStats(Plugin):
    name = _("Events statistics")
    description = _("Basic statistics for events")
    author = "Piotrek Wasilewski"
    
    def widgets(self):
        return [EventsStatsWidget]
    
__plugins__ = [EventsStats]
