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

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from IPy import IP 

def IPv6_validation(value):
    try:
        ip_version = IP(value).version()
        if ip_version !=6:
            raise ValidationError(u'%s is not a correct IPv6 address' % value)
    except ValueError:
        raise ValidationError(u'%s is not a correct IPv6 address' % value)

def IPv4_validation(value):
    try:
        ip_version = IP(value).version()
        if ip_version !=4:
            raise ValidationError(u'%s is not a correct IPv4 address' % value)
    except ValueError:
        raise ValidationError(u'%s is not a correct IPv4 address' % value)
    
