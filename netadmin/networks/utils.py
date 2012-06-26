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
from netaddr import *

def IPv6_validation(value):
	
    try:
        ip_version = IPAddress(value).version
        if ip_version !=6:
            raise ValidationError(u'%s is not a correct IPv6 address' % value)
    except ValueError:
        raise ValidationError(u'%s is not a correct IPv6 address' % value)

def IPv4_validation(value):
    
    try:
        ip_version = IPAddress(value).version
        if ip_version !=4:
            raise ValidationError(u'%s is not a correct IPv4 address' % value)
    except ValueError:
        raise ValidationError(u'%s is not a correct IPv4 address' % value)

def get_subnet(host_list,sub,add):
    subnet_ip = []
    render_hosts = []
    find_host = []
    subnet_ip  = [add,sub]
    subnet_ip = "/".join(subnet_ip)
    ip = IPNetwork(subnet_ip)
    
    for x in ip:
        render_hosts.append(str(x))
    
    for user_host in host_list:
        for render_host in render_hosts:
            if user_host.ipv4 == render_host or user_host.ipv6 == render_host:
                find_host.append(user_host)
    return find_host
    


    
