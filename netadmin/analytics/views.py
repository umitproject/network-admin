#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Amit Pal <amix.pal@gmail.com>
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

from django.http import HttpResponse
from django.views.generic.simple import direct_to_template

from netadmin.shortcuts import  get_events, get_hosts, get_eventtypes
from netadmin.events.models import EventType, Event
from utils import get_host_count

def event_analysis(request):
	event_host, event_alerts = ([] for x in range(2))
	event_alerts.append(['Host Name', 'No. of Events'])
	host_ipv4 = [et for et in get_hosts(user=request.user)]
	event = get_events(source_hosts=host_ipv4)
	for x in host_ipv4:
		event_host.append(x.ipv4)
		event_alerts.append([x.ipv4.encode('utf8'),get_host_count(x,event)])
	extra_context = {
	'event_data': event_alerts
	}
	return direct_to_template(request, 'analytics/graph_base.html',
	                           extra_context=extra_context)
	                      
def alert_analysis(request):
	low,medium, high = ([get_eventtypes(request.user, x) for x in (1,2,3)])
	extra_context = {
	'low':len(low),
	'medium':len(medium),
	'high':len(high)
	}
	return direct_to_template(request, 'analytics/graph_alert.html',
					          extra_context=extra_context)
					    
