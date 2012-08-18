#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Amit Pal <amix.pal@gmail.com>
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


urlpatterns = patterns('netadmin.users.views',
    url(r'^search/$', 'user_search', name='user_search'),
    url(r'^users/$', 'user_list', name='user_list'),
    url(r'^profile/$', 'user_private', name='user_profile_private'),
    url(r'^settings/(?P<slug>\w+)/$', 'notification_setting', name='notification_setting'),
    url(r'^public/(?P<slug>\w+)/$', 'user_public', name='user_profile_public'),
    url(r'^register/$', 'user_register', name='user_register'),
    url(r'^password_change/(?P<id>\w+)$', 'user_change_password', name='user_change_password'),
    url(r'^staff_change/(?P<id>\w+)$', 'user_change_status', name='user_change_status'),
    url(r'^user_block/(?P<id>\w+)$', 'user_block', name='user_block'),
    url(r'^activate/(?P<code>\w+)/$', 'user_activation', name='user_activation'),
    url(r'^refresh_access_token/$', 'refresh_access_token', name='refresh_access_token'),
    url(r'^remove_inactive_users/$', 'remove_inactive_users', name='remove_inactive_users'),
)
