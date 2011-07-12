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
from piston.authentication import HttpBasicAuthentication

from netadmin.webapi.handlers import *


# set up basic authentication
auth = HttpBasicAuthentication()
ad = { 'authentication': auth }

# apply authentication to all resources
host_handler = Resource(HostHandler, **ad)
event_handler = Resource(EventHandler, **ad)
net_handler = Resource(NetworkHandler, **ad)

urlpatterns = patterns('netadmin.webapi.views',
    # Host handler
    url(r'^host/(?P<host_id>\d+)/$', host_handler, name='api_host_detail'),
    url(r'^host/list/$', host_handler, name='api_host_list'),
    
    # Network handler
    url(r'^network/(?P<network_id>\d+)/$', net_handler, name='api_network_detail'),
    url(r'^network/list/$', net_handler, name='api_network_list'),
    
    # Event handler
    url(r'^event/report/$', event_handler, name='api_report_event'),
    url(r'^event/(?P<event_id>\d+)/$', event_handler, name='api_event_detail'),
    url(r'^event/list/$', event_handler, name='api_event_list'),
)
