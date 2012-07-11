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


urlpatterns = patterns('netadmin.networks.views',
    url(r'^host/(?P<object_id>\d+)/$',
        'host_detail', name='host_detail'),
    url(r'^host/list/$',
        'host_list', name='host_list'),
    url(r'^host/list/page/(?P<page>\d+)/$',
        'host_list', name='host_list_page'),
    url(r'^host/new/$',
        'host_create', name="host_new"),
    url(r'^host/edit/(?P<object_id>\d+)/$',
        'host_update', name="host_update"),
    url(r'^host/delete/(?P<object_id>\d+)/$',
        'host_delete', name="host_delete"),
    
    url(r'^network/(?P<object_id>\d+)/$',
        'network_detail', name='network_detail'),
    url(r'^network/list/$',
        'network_list', name='network_list'),
    url(r'^network/list/page/(?P<page>\d+)/$',
        'network_list', name='network_list_page'),
    url(r'^network/new/$',
        'network_create', name="network_new"),
    url(r'^network/edit/(?P<object_id>\d+)/$',
        'network_update', name="network_update"),
    url(r'^network/delete/(?P<object_id>\d+)/$',
        'network_delete', name="network_delete"),
    url(r'^network/events/(?P<object_id>\d+)/$',
        'network_events', name='network_events'),
    
    url(r'^network/netmask-create/$',
        'subnet_network', name='subnet_network'),
    url(r'/update/(?P<object_id>\d+)/$',
        'network_select', name='network_select'),
    
     url(r'^host/trace/route/(?P<object_id>\d+)/$',
        'trace_route', name="trace_route"),
    
                           
    url(r'share/list/(?P<object_type>host|network)/(?P<object_id>\d+)/',
        'share_list', name="share_list"),
    url(r'share/(?P<object_type>host|network)/(?P<object_id>\d+)/',
        'share', name="share"),
    url(r'share/not/(?P<object_type>host|network)/(?P<object_id>\d+)/(?P<user_id>\d+)/',
        'share_not', name="share_not"),
    url(r'share/edit/(?P<object_type>host|network)/(?P<object_id>\d+)/(?P<user_id>\d+)/',
        'share_edit', name="share_edit"),
)
