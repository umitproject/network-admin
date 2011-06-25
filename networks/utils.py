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

from networks.models import Host, Network, HostAccess, NetworkAccess

def user_has_access(obj, user):
    if obj.__class__ not in [Host, Network]:
        return False
    
    if obj.user == user:
        return True
    
    if obj.__class__ == Host:
        try:
            ac = HostAccess.objects.get(user=user, host=obj)
        except HostAccess.DoesNotExist:
            return False
        return True
    
    if obj.__class__ == Network:
        try:
            ac = NetworkAccess.objects.get(user=user, network=obj)
        except NetworkAccess.DoesNotExist:
            return False
        return True

def user_can_edit(obj, user):
    if obj.__class__ not in [Host, Network]:
        return False
    
    if obj.user == user:
        return True
    
    if obj.__class__ == Host:
        try:
            ac = HostAccess.objects.get(user=user, host=obj)
        except HostAccess.DoesNotExist:
            return False
        if ac.edit == True:
            return True
        else:
            return False
    
    if obj.__class__ == Network:
        try:
            ac = NetworkAccess.objects.get(user=user, network=obj)
        except NetworkAccess.DoesNotExist:
            return False
        if ac.edit == True:
            return True
        else:
            return False

def filter_by_user(model, user):
    if model not in [Host, Network]:
        return None
    
    if model == Host:
        pks = [ac.host.pk for ac in HostAccess.objects.filter(user=user)]
        hosts = []
        for h in Host.objects.all().only('id'):
            if h.user == user or h.pk in pks:
                hosts.append(h.pk)
        return Host.objects.filter(pk__in=hosts)
    
    if model == Network:
        pks = [ac.network.pk for ac in NetworkAccess.objects.filter(user=user)]
        networks = []
        for n in Network.objects.all().only('id'):
            if n.user == user or n.pk in pks:
                networks.append(n.pk)
        return Network.objects.filter(pk__in=networks)
