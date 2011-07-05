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
