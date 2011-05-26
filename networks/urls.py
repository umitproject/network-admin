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
from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.create_update import *
from networks.models import Host
from networks.forms import *

host_queryset = Host.objects.all()

host_delete_args = {
    'model': Host,
    #it would be better to use reverse_lazy here (it is not supported yet):
    'post_delete_redirect': '/network/host/list/'
}

host_update_args = {
    'form_class': HostUpdateForm,
    'template_name': 'networks/host_update.html'
}

urlpatterns = patterns('networks.views',
   url(r'^host/(?P<object_id>\d+)/$', object_detail, {'queryset': host_queryset}, name='host_detail'),
   url(r'^host/list/$', object_list, {'queryset': host_queryset}, name='host_list'),
   url(r'^host/new/$', create_object, {'form_class': HostCreateForm}, name="host_new"),
   url(r'^host/edit/(?P<object_id>\d+)/$', update_object, host_update_args, name="host_update"),
   url(r'^host/delete/(?P<object_id>\d+)/$', delete_object, host_delete_args, name="host_delete")
)
