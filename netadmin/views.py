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

from django.views.generic.simple import direct_to_template

try:
    from search.core import search
except ImportError:
    search = None

from events.models import Event
from networks.models import Host, Network
from permissions.utils import user_has_access


RESULTS_LIMIT = 10


def global_search(request):
    extra_context = {}
    
    if request.method == 'GET' and search != None:
        search_phrase = request.GET.get('s')
        if search_phrase:
            events = search(Event, search_phrase)
            event = events.order_by('-timestamp')
            events = filter(lambda e: user_has_access(e.source_host, request.user), events)
            
            hosts = search(Host, search_phrase).filter(user=request.user)
            networks = search(Network, search_phrase).filter(user=request.user)
            extra_context = {
                'events': events[:RESULTS_LIMIT],
                'hosts': hosts[:RESULTS_LIMIT],
                'networks': networks[:RESULTS_LIMIT]
            }
            
    return direct_to_template(request, 'global_search.html',
                              extra_context=extra_context)