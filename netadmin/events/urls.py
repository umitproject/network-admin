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


urlpatterns = patterns('netadmin.events.views',
    url(r'^(?P<object_id>\d+)/$',
        'event_detail', name='event_detail'),
    url(r'^message/(?P<message_slug>[-\w]+)/$',
        'event_detail', name='event_detail'),
    url(r'^check/(?P<object_id>\d+)/$',
        'event_check', name='event_check'),
    
    url(r'^list/$',
        'events_list', name='events_list'),
    url(r'^list/page/(?P<page>\d+)/$',
        'events_list', name='event_list_page'),
    
    url(r'^alerts/$',
        'events_alerts', name='events_alerts'),
    url(r'^alerts/(?P<alert_level_id>\d+)/$',
        'events_alerts', name='event_alert_level'),
    url(r'^alerts/(?P<alert_level_slug>[-\w]+)/$',
        'events_alerts', name='event_alert_level'),
    
    url(r'^date/(?P<year>\d+)/$',
        'events_date', name='events_date'),
    url(r'^date/(?P<year>\d+)/(?P<month>\d+)/$',
        'events_date', name='events_date'),
    url(r'^date/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$',
        'events_date', name='events_date'),
    
    url(r'^type/edit/$',
        'eventtype_edit', name='eventtype_edit'),
    url(r'^type/(?P<event_type_id>\d+)/$',
        'eventtype_detail', name='eventtype_detail'),
    url(r'^type/(?P<event_type_slug>[-\w]+)/$',
        'eventtype_detail', name='eventtype_detail'),
    
     url(r'^categ/$',
        'eventcateg_detail', name='eventcateg_detail'),
     url(r'^categ/(?P<categ_id>\d+)/$',
        'categ_detail', name='categ_detail'),
     url(r'^categ/delete/(?P<categ_id>\d+)/$',
        'categ_delete', name="categ_delete"),
    
     url(r'^comment/(?P<object_id>\d+)$',
        'comment_detail', name='comment_detail'),
    url(r'^comment/$',
        'event_comment', name=" event_comment"),
     
        
    
    
    
    url(r'^ajax/$',
        'events_ajax', name='event_ajax'),
   
    url(r'^search/$',
        'events_search', name='event_search'),
    
    url(r'^stats/$',
        'events_stats', name='events_stats'),
   
)
