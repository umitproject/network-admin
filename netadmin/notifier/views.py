#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors: Amit Pal <amix.pal@gmail.com>
#          Piotrek Wasilewski <wasilewski.piotrek@gmail.com>
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

from utils import dispatcher
from models import Notifier
	
def dispatch_notify(request, user, notification_type, notify_type):
	"""
	Send the notification on the behalf of user priority
	"""
	
	if notify_type == 0 and 1:
		notifier = Notifier.objects.get(user=user.username).low
	elif notify_type == 2:
		notifier = Notifier.objects.get(user=user.username).medium
	elif notify_type == 3:
		notifier = Notifier.objects.get(user=user.username).high
	notifier_type = get_notifier(notifier)
	dispatcher.dispatch(notifier_type, notification_type, clear=True, user)
	return HttpResponse("<p> Done </p>")


def dispatch_all(request):
    """Sends all notifications using Dispatcher
    """
    dispatcher.dispatch()
    return HttpResponse("<p>Done</p>")