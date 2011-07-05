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

from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import redirect_to

def user_detail(request, slug):
    
    user = User.objects.get(username=slug)
    
    if request.method == 'POST':
        user_permissions = request.POST.getlist('user_perms')
        
        all_permissions = Permission.objects.all()
        required_permissions = ['host', 'network', 'report meta']
        permissions = [p for p in all_permissions if p.content_type.name in required_permissions]
        
        for perm in permissions:
            if perm.pk not in user_permissions:
                pass
    
    permissions = Permission.objects.all()
    user_perms = []
    for perm in permissions:
        if user.has_perm(perm):
            user_perms.append(perm)
        
    user_detail_args = {
        'slug': slug,
        'queryset': User.objects.all(),
        'template_name': 'users/user_detail.html',
        'slug_field': 'username',
        'extra_context': {
            'permissions': Permission.objects.all(),
            'user_permissions': user_perms,
            'required_permissions': ['host', 'network', 'report meta']
        }
    }
    
    return object_detail(request, **user_detail_args)