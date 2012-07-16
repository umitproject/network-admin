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
from Skype4Py import Skype
import sys


from netadmin.events.models import EventType, AlertCount
from netadmin.shortcuts import get_alert_events, get_notifier

def send_notification(request):
	high, low, medium = ([] for i in range(3))
	low,medium, high = ([get_alert_events(x) for x in (1,2,3)])
	alert_count = AlertCount.objects.get(user=request.user.username)
	l_al,m_al,h_al = alert_count.low, alert_count.medium, alert_count.high
	if len(low)>=l_al:
		low_notifier = get_notifier(request.user.username).low_notify
		notify(request, low_notifier)
	elif len(medium)>=m_al:
		medium_notifier = get_notifier(request.user.username).medium_notify
		notify(request, medium_notifier)
	elif len(high)>=h_al:
		high_notifier = get_notifier(request.user.username).high_notify
		notify(request, high_notifier)
	return HttpResponse()
	
def notify(request,notify_type):
	if notify_type == 0:
		send_emails(request)
	elif notify_type == 1:
		send_skype(request)
	elif notify_type == 2:
		send_irc(request)

def send_emails(request):
	return

def send_skype(request):
	return

def send_irc(request):
	return
	
	
