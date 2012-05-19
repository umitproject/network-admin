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

import random
import time

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

try:
    from search.core import search
except ImportError:
    search = None
from piston.models import Consumer, Token

from django.conf import settings
from forms import UserForm, UserProfileForm, UserRegistrationForm
from models import UserActivationCode
from django.contrib.auth.forms import AdminPasswordChangeForm


ACTIVATION_MAIL_SUBJECT = _("Activate your account in Network Administrator")
ACTIVATION_MAIL_CONTENT = _("""
    To finish registration just click the activation link below:
    
    %s
    
    --
    Network Administrator Team
    www.umitproject.org
""")


@login_required
def user_public(request, slug):
    user = get_object_or_404(User, username=slug)
    if not user.get_profile().is_public:
        return HttpResponseForbidden()
    
    return object_detail(request, slug=slug, queryset=User.objects.all(),
                         slug_field='username',
                         template_name='users/user_public.html')

@login_required
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

    try:
        api_consumer = Consumer.objects.get(user=request.user)
    except Consumer.DoesNotExist:
        api_consumer = Consumer.objects.create(user=request.user,
                                               status='accepted')
        api_consumer.generate_random_codes()

    try:
        api_access_token = api_consumer.token_set.get(token_type=Token.ACCESS,
                                                      user=request.user)
    except Token.DoesNotExist:
        api_access_token = Token.objects.create(user=request.user,
            consumer=api_consumer, is_approved=True, timestamp=time.time(),
            token_type=Token.ACCESS)
        api_access_token.generate_random_codes()
        
    extra_context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'api_consumer': api_consumer,
        'api_access_token': api_access_token
    }
    
    return object_detail(request, object_id=request.user.pk,
                         queryset=User.objects.all(),
                         template_name='users/user_private.html',
                         extra_context=extra_context)

@login_required
def user_list(request, page=None):
    user_status = request.user.is_staff
    if user_status:
        users_list = User.objects.all()
        paginator = Paginator(list(users_list), 10)
        page = page or request.GET.get('page', 1)
        try:
            users_list = paginator.page(page)
        except PageNotAnInteger:
            users_list = paginator.page(1)
        except EmptyPage:
            users_list = paginator.page(paginator.num_pages)
        extra_context = { 
            'users_list': users_list
        }
        return direct_to_template(request, 'users/user_list.html',
                              extra_context = extra_context)
    else:
        raise Http404
    
@login_required
def user_search(request):
    if search != None:
        users = None
        search_phrase = request.GET.get('s')
        if search_phrase:
            users = search(User, search_phrase)

        extra_context = {
            'users': users
        }
    else:
        extra_context = {}
        
    return direct_to_template(request, 'users/user_search.html',
                              extra_context=extra_context)
    
def user_register(request, template_name="users/user_registration.html"):
    registration_form = UserRegistrationForm()
    if request.method == 'POST':
        registration_form = UserRegistrationForm(request.POST)
        if registration_form.is_valid():
            user = registration_form.save()
            # generate random activation code
            random.seed()
            code = random.getrandbits(128)
            activation = UserActivationCode(user=user, code=code)
            activation.save()
            
            code_url = reverse('user_activation', args=[code])
            activation_url = "http://%s%s" % (settings.SITE_DOMAIN, code_url)
            send_mail(ACTIVATION_MAIL_SUBJECT,
                      ACTIVATION_MAIL_CONTENT % activation_url,
                      settings.ACTIVATION_FROM_EMAIL, [user.email])
            
            return direct_to_template(request,
                        "users/user_registration_confirm.html")
    extra_context = {
        'registration_form': registration_form
    }
    return direct_to_template(request, template_name,
                              extra_context=extra_context)
    
def user_activation(request, code,
                    template_name="users/user_activation.html"):
    try:
        activation = UserActivationCode.objects.get(code=code)
        active = activation.is_active()
    except UserActivationCode.DoesNotExist:
        activation = active = False
    if active:
        user = activation.user
        user.is_active = True
        user.save()
        try:
            consumer = Consumer.objects.get(user=user)
        except Consumer.DoesNotExist:
            consumer = Consumer(name=user.username, user=user,
                                status='accepted')
            consumer.generate_random_codes()
            consumer.save()
        
        try:
            token = Token.objects.get(user=user, consumer=consumer)
        except Token.DoesNotExist:
            token = Token(user=user, consumer=consumer, is_approved=True,
                          timestamp=time.time(),
                          token_type=Token.ACCESS)
            token.generate_random_codes()
            token.save()
        
    extra_context = {
        'active': active,
        'activation': activation
    }
    return direct_to_template(request, template_name,
                              extra_context=extra_context)

@login_required
def refresh_access_token(request):
    token = Token.objects.get(user=request.user, token_type=Token.ACCESS)
    token.generate_random_codes()
    token.save()
    return user_private(request)

def remove_inactive_users(request):
    codes = UserActivationCode.objects.all()
    counter = 0
    for code in codes:
        if not code.is_active():
            user = code.user
            user.delete()
            code.delete()
            counter += 1
    return HttpResponse('Removed %i accounts' % counter)

@login_required
def user_change_password(request, id):
    user = User.objects.get(pk=id)
    form = AdminPasswordChangeForm(user, request.POST)
    if form.is_valid():
        new_user = form.save()
        msg = _('Password changed successfully.')
        request.user.message_set.create(message=msg)
        return HttpResponseRedirect('../../user/users')
    else:
        form = AdminPasswordChangeForm(user)
    extra_context = {
        
        'form': form,
        'change': True
        }
    return direct_to_template(request,"users/user_password_change.html",
                extra_context = extra_context)
                
@login_required
def user_change_status(request, id):
    user = User.objects.get(pk=id)
    if user.is_staff:
        user.is_staff = False
    else:
        user.is_staff = True
    user.save()
    return HttpResponseRedirect('../../user/users')
    
@login_required        
def user_block(request, id):
    user = User.objects.get(pk=id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    return HttpResponseRedirect('../../user/users')    
