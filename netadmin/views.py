#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Adriano Monteiro Marques
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

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template, redirect_to

from netadmin.forms import SearchForm
from netadmin.events.models import Event
from netadmin.networks.models import Host, Network


def home(request):
    """Home page

    """
    if request.user.is_authenticated():
        return direct_to_template(request, template='home.html')
    else:
        return redirect_to(request, url=reverse('login_page'))

@login_required
def search(request):
    if 'haystack' in settings.INSTALLED_APPS:
        return search_haystack(request)
    elif 'search' in settings.INSTALLED_APPS:
        return search_nonrel(request)
    else:
        return direct_to_template(request, template='home.html')

def search_haystack(request):

    """Search using Haystack

    """

    from haystack.query import SearchQuerySet

    query = request.GET.get('q')

    results = SearchQuerySet().filter(content=query)

    context = {
        'query': query,
        'results': results,
        'form': SearchForm(request.GET)
    }

    return direct_to_template(request, extra_context=context,
                              template='search.html')

def search_nonrel(request):

    """Search using Nonrel-search

    """

    from search.core import search

    query = request.GET.get('q')

    if query:
        events = search(Event, query).order_by('-timestamp')
        events = filter(lambda e: e.source_host.has_access(request.user), events)

        hosts = search(Host, query)
        hosts = filter(lambda h: h.has_access(request.user), hosts)
        
        networks = search(Network, query)
        networks = filter(lambda n: n.has_access(request.user), networks)

        context = {
            'results_events': events,
            'results_hosts': hosts,
            'results_networks': networks,
            'query': query,
            'form': SearchForm(request.GET)
        }
    else:
        context = {
            'form': SearchForm(request.GET)
        }

    return direct_to_template(request, extra_context=context,
                              template='search_nonrel.html')
