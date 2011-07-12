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

from netadmin.events.models import Event


urlpatterns = patterns('netadmin.events.views',
   url(r'^(?P<object_id>\d+)/$', 'event_detail', name='event_detail'),
   url(r'^check/(?P<object_id>\d+)/$', 'event_check', name='event_check'),
   url(r'^list/$', 'events_list', name='event_list'),
   url(r'^list/page/(?P<page>\d+)/$', 'events_list', name='event_list_page'),
   
   url(r'^search/$', 'events_search', name='events_search'),
   
   url(r'^alerts/level/(?P<level_id>\d+)/$', 'alerts_list', name='alerts_list'),
   url(r'^alerts/edit/$', 'alerts_edit', name='alerts_edit'),
   url(r'^alerts/remove/(?P<object_id>\d+)/$', 'alerts_edit', name='alerts_remove')
)