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
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Permission
from django.views.generic.create_update import *
from django.views.generic.list_detail import object_list, object_detail

urlpatterns = patterns('users.views',
    url(r'^list/$', object_list, {'queryset': User.objects.all(), 'template_name': 'users/user_list.html'},
        name='users_list'),
    url(r'^(?P<slug>\w+)/$', 'user_detail', name='users_detail'),
    url(r'^new/$', create_object, {'form_class': UserCreationForm, 'template_name': 'users/user_form.html'},
        name='users_new'),
)