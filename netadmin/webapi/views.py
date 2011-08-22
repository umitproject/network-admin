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

try:
    import simplejson as json
except ImportError:
    import json
    
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from piston.authentication import oauth_access_token
from piston.models import Consumer, Token
from piston import oauth

def api_response(response):
    """Returns JSON generated from Python data structure""" 
    return HttpResponse(json.dumps(response))

def api_msg(status, message):
    """Returns status message"""
    response = {
        'status': status,
        'message': message
    }
    return api_response(response)

def api_error(message):
    """Returns error message"""
    return api_msg('error', message)

def api_ok(message):
    """Returns message with status OK"""
    return api_msg('ok', message)

def xauth_callback(request):
    x_auth_mode = request.POST.get('x_auth_mode')
    
    if x_auth_mode and x_auth_mode == 'client_auth':
        username = request.POST.get('x_auth_username')
        password = request.POST.get('x_auth_password')
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return api_error(_("Authentication error"))
        
        try:        
            consumer = Consumer.objects.get(user=user)
        except Consumer.DoesNotExist:
            return api_error(_("Authentication error"))
        
        try:
            token = Token.objects.get(user=user, consumer=consumer,
                token_type=Token.ACCESS)
        except Token.DoesNotExist:
            return api_error(_("Authentication error"))
        
        token_dict = {
            'oauth_token': token.key,
            'oauth_token_secret': token.secret
        }
        return api_ok(token_dict)
    
    return oauth_access_token(request)
