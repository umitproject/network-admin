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

import random

from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext as _
from search.core import search

from netadmin.users.forms import UserForm, UserProfileForm, \
    UserRegistrationForm
from netadmin.users.models import UserActivationCode


def user_public(request, slug):
    user = get_object_or_404(User, username=slug)
    if not user.get_profile().is_public:
        return HttpResponseForbidden()
    
    return object_detail(request, slug=slug, queryset=User.objects.all(),
                         slug_field='username',
                         template_name='users/user_public.html')

def user_private(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST,
                                       instance=request.user.get_profile())
        
        # Forms are displayed together thus both of them
        # should be valid before saving the whole user data
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile =  profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
    
    user_profile = request.user.get_profile()
    profile_form = UserProfileForm(instance=user_profile)
    user_form = UserForm(instance=request.user)
        
    extra_context = {
        'profile_form': profile_form,
        'user_form': user_form
    }
    
    return object_detail(request, object_id=request.user.pk,
                         queryset=User.objects.all(),
                         template_name='users/user_private.html',
                         extra_context=extra_context)
    
def user_search(request):
    users = None
    search_phrase = request.GET.get('s')
    if search_phrase:
        users = search(User, search_phrase)
        
    extra_context = {
        'users': users
    }
        
    return direct_to_template(request, 'users/user_search.html',
                              extra_context=extra_context)
    
def user_register(request, template_name="users/user_registration.html"):
    if request.method == 'POST':
        registration_form = UserRegistrationForm(request.POST)
        if registration_form.is_valid():
            user = registration_form.save()
            # generate random activation code
            random.seed()
            code = random.getrandbits(128)
            activation = UserActivationCode(user=user, code=code)
            activation.save()
            return user_register_confirm(request, activation.code)
    registration_form = UserRegistrationForm()
    extra_context = {
        'registration_form': registration_form
    }
    return direct_to_template(request, template_name,
                              extra_context=extra_context)
    
def user_register_confirm(request, code=None,
                          template_name="users/user_registration_confirm.html"):
    if code:
        activation = UserActivationCode.objects.get(code=code)
    else:
        activation = None
    extra_context = {
        'activation': activation
    }
    return direct_to_template(request, template_name,
                              extra_context=extra_context)
    
def user_activation(request, code,
                    template_name="users/user_activation.html"):
    activation = UserActivationCode.objects.get(code=code)
    active = activation.is_active()
    if active:
        user = activation.user
        user.is_active = True
        user.save()
    extra_context = {
        'active': active,
        'activation': activation
    }
    return direct_to_template(request, template_name,
                              extra_context=extra_context)