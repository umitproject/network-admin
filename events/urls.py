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

from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_detail, object_list
from events.models import Event

object_detail = login_required(object_detail)
object_list = login_required(object_list)

event_queryset = Event.objects.all().order_by('timestamp')

event_list_args = {
    'queryset': event_queryset,
    'paginate_by': 20,
    'extra_context': {'url': '/event/list/'}
}

urlpatterns = patterns('events.views',
   url(r'^(?P<object_id>\d+)/$', object_detail, {'queryset': event_queryset}, name='event_detail'),
   url(r'^list/$', object_list, event_list_args, name='event_list'),
   url(r'^list/page/(?P<page>\d+)/$', object_list, event_list_args, name='event_list_page')
)