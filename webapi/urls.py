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
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication, NoAuthentication
from webapi.handlers import *

auth = HttpBasicAuthentication()
ad = { 'authentication': auth }

host_handler = Resource(HostHandler, **ad)
event_handler = Resource(EventHandler, **ad)

urlpatterns = patterns('webapi.views',
   url(r'^host/(?P<host_id>\d+)/$', host_handler, name='host_detail'),
   url(r'^host/list/$', host_handler, name='host_list'),
   url(r'^event/report/$', event_handler, name="report_event"),
   url(r'^event/(?P<event_id>\d+)/$', event_handler),
   url(r'^event/list/$', event_handler),
)
