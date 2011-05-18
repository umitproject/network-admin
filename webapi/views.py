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

import json
from django.http import HttpResponse

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
