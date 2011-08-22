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
from datetime import timedelta

from django.utils.translation import ugettext as _

from netadmin.plugins import Plugin, Widget
from netadmin.plugins.options import get_option
from netadmin.shortcuts import get_host, get_hosts, get_alerts, get_events, \
    get_networks, get_network
from netadmin.utils.charts import ColumnChart, NumberColumn, DateColumn
from netadmin.utils.timehelper import date_iterator 


class HostWidget(Widget):
    name = _("Host details")
    description = _("Shows basic data for the host")
    template_name = 'host_widget.html'
    
    DAYS_CHOICES = [(i,i) for i in xrange(1,31)]
    SHOW_CHOICES = [('yes', _('Yes')), ('no', _('No'))]
    
    def get_title(self, widget):
        host = self.get_option('host_detail_widget_host', widget)
        return "%s's details" % host.name.capitalize()
    
    def options(self, widget):
        hosts = get_hosts(widget.user)
        return  {
            'host_detail_widget_host': {
                'label': _("Host"),
                'choices': [(h.pk, h.name) for h in hosts],
                'default': hosts[0].pk if hosts else 0,
                'return_func': lambda value: get_host(value)
            },
            'host_detail_widget_days': {
                'label': _("Days"),
                'choices': self.DAYS_CHOICES,
                'default': 1,
                'return_func': lambda value: int(value)
            },
            'host_detail_widget_alerts': {
                'label': _("Show alerts"),
                'choices': self.SHOW_CHOICES,
                'default': 'yes',
                'return_func': lambda value: True if value == 'yes' else False
            },
            'host_detail_widget_chart': {
                'label': _("Show chart"),
                'choices': self.SHOW_CHOICES,
                'default': 'yes',
                'return_func': lambda value: True if value == 'yes' else False
            },
        }
        
    def context(self, widget):
        days = self.get_option('host_detail_widget_days', widget)
        date_from = datetime.date.today() - timedelta(days=days-1)
        days_range = list(date_iterator(date_from))
        
        host = self.get_option('host_detail_widget_host', widget)
        events_count = []
        for day in days_range: 
            next_day = day + timedelta(days=1)
            events = get_events(source_hosts=[host], time_from=day, time_to=next_day)
            events_count.append(events.count())
        
        chart = ColumnChart(_("Number of events per day"))
        chart.add_column(_("Day"), days_range, DateColumn)
        chart.add_column(_("Number of events"), events_count, NumberColumn)
        
        return {
            'host_chart': chart,
            'host': host,
            'show_chart': self.get_option('host_detail_widget_chart', widget),
            'show_alerts': self.get_option('host_detail_widget_alerts', widget)
        }
        
class NetworkWidget(Widget):
    name = _("Network details")
    description = _("Shows basic data for the network")
    template_name = 'network_widget.html'
    
    DAYS_CHOICES = [(i,i) for i in xrange(1,31)]
    SHOW_CHOICES = [('yes', _('Yes')), ('no', _('No'))]
    
    def get_title(self, widget):
        network = self.get_option('network_detail_widget_network', widget)
        return "%s's details" % network.name.capitalize()
    
    def options(self, widget):
        networks = get_networks(widget.user)
        return  {
            'network_detail_widget_network': {
                'label': _("Network"),
                'choices': [(n.pk, n.name) for n in networks],
                'default': networks[0].pk if networks else 0,
                'return_func': lambda value: get_network(value)
            },
            'network_detail_widget_days': {
                'label': _("Days"),
                'choices': self.DAYS_CHOICES,
                'default': 1,
                'return_func': lambda value: int(value)
            },
            'network_detail_widget_chart': {
                'label': _("Show chart"),
                'choices': self.SHOW_CHOICES,
                'default': 'yes',
                'return_func': lambda value: True if value == 'yes' else False
            },
        }
        
    def context(self, widget):
        days = self.get_option('network_detail_widget_days', widget)
        date_from = datetime.date.today() - timedelta(days=days-1)
        days_range = list(date_iterator(date_from))
        
        network = self.get_option('network_detail_widget_network', widget)
        events_count = []
        for day in days_range: 
            next_day = day + timedelta(days=1)
            hosts = network.hosts()
            events = get_events(source_hosts=hosts, time_from=day, time_to=next_day)
            events_count.append(events.count())
        
        chart = ColumnChart(_("Number of events per day"))
        chart.add_column(_("Day"), days_range, DateColumn)
        chart.add_column(_("Number of events"), events_count, NumberColumn)
        
        return {
            'network_chart': chart,
            'network': network,
            'show_chart': self.get_option('network_detail_widget_chart', widget),
            'show_alerts': self.get_option('network_detail_widget_alerts', widget)
        }

class NetworksTools(Plugin):
    name = _("Networks tools")
    description = _("Basic tools for hosts and networks")
    author = "Piotrek Wasilewski"
    
    def actions(self):
        return [
            ("network_list_table_head", lambda n: _("Number of hosts")),
            ("network_list_table_cell", lambda n: n.hosts().count())
        ]
        
    def widgets(self):
        return [HostWidget, NetworkWidget]
    
__plugins__ = [NetworksTools]