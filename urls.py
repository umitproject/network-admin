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
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
    (r'^api/', include('netadmin.webapi.urls')),
    (r'^network/', include('netadmin.networks.urls')),
    (r'^event/', include('netadmin.events.urls')),
    (r'^report/', include('netadmin.reportmeta.urls')),
    (r'^user/', include('netadmin.users.urls')),
    (r'^plugins/', include('netadmin.plugins.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^search/', 'netadmin.views.global_search', name='global_search'),
    
    url(r'login/', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}, name='login_page'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout'),

    url(r'^oauth/request_token/$','piston.authentication.oauth_request_token'),
    url(r'^oauth/authorize/$','piston.authentication.oauth_user_auth'),
    url(r'^oauth/access_token/$','netadmin.webapi.views.xauth_callback'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': settings.STATIC_ROOT})
    )
