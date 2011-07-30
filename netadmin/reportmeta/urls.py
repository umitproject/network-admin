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
from django.views.generic.create_update import delete_object

from netadmin.reportmeta.models import ReportMeta


urlpatterns = patterns('netadmin.reportmeta.views',
    url(r'^$', 'reports', name='reports'),
    url(r'^(?P<object_id>\d+)/$', 'reportmeta_detail', name='reportmeta_detail'),
    url(r'^get/(?P<object_id>\d+)/$', 'reportmeta_get_report', name='reportmeta_get_report'),
    url(r'^list/(?P<object_type>host|network)/$', 'reportmeta_list', name='reportmeta_list'),
    url(r'^new/(?P<object_type>host|network)/$', 'reportmeta_new', name="reportmeta_new"),
    url(r'^new/(?P<object_type>host|network)/(?P<object_id>\d+)/$', 'reportmeta_new_from_object', name="reportmeta_new"),
    url(r'^edit/(?P<object_id>\d+)/$', 'reportmeta_update', name="reportmeta_update"),
    url(r'^delete/(?P<object_id>\d+)/$', 'reportmeta_delete', name="reportmeta_delete"),
    url(r'^send/emails/$', 'reportmeta_send_emails', name="reportmeta_send_emails"),
)
