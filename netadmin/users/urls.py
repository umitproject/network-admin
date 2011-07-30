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


urlpatterns = patterns('netadmin.users.views',
    url(r'^search/$', 'user_search', name='user_search'),
    url(r'^profile/$', 'user_private', name='user_profile_private'),
    url(r'^public/(?P<slug>\w+)/$', 'user_public', name='user_profile_public'),
    url(r'^register/$', 'user_register', name='user_register'),
    url(r'^confirm/$', 'user_register_confirm', name='user_register_confirm'),
    url(r'^activate/(?P<code>\w+)/$', 'user_activation', name='user_activation'),
)