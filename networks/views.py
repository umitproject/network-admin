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

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.generic.create_update import create_object
from django.views.generic.list_detail import object_detail, object_list
from events.models import Event
from networks.models import Host, Network, NetworkHost
from networks.forms import HostCreateForm

from search.core import search

@login_required
def host_list(request, page=None):
    
    host_queryset = Host.objects.all()
    
    if request.GET.get('search'):
        search_phrase = request.GET.get('search')
        host_queryset = Host.objects.none()
        search_results = search(Host, search_phrase)
    else:
        search_results = None

    kwargs = {
        'queryset': host_queryset,
        'paginate_by': 15,
        'extra_context': {'url': reverse('host_list'),
                          'search_results': search_results}
    }
    return object_list(request, page=page, **kwargs)

@login_required
def host_create(request):
    form_class = HostCreateForm(initial={'user': request.user.pk})
    return create_object(request, form_class=form_class)

@login_required
def network_detail(request, object_id):
    """
    Network detail page has the following features:
        * displaying basic network info (name, description, etc.)
        * listing hosts related to network
        * creating relations between network and host
        * removing relations between network and host(s)
    """
    
    network = Network.objects.get(pk=object_id)
    
    # remove relation between the network and selected host(s)
    if request.POST.getlist('remove_host'):
        hosts_pk = request.POST.getlist('remove_host')
        network_host = NetworkHost.objects.filter(network=network, host__pk__in=hosts_pk)
        network_host.delete()
    
    # create relation between the network and selected host
    if request.POST.get('add_host'):
        host = Host.objects.get(pk=request.POST.get('add_host'))
        network_host = NetworkHost(network=network, host=host)
        network_host.save()
    
    queryset = Network.objects.all()
    if network.has_hosts():
        hosts_ids = [host.pk for host in network.get_hosts()]
        hosts_other = Host.objects.exclude(pk__in=hosts_ids)
    else:
        hosts_other = Host.objects.all()
    extra_context = {
        'hosts_other': hosts_other
    }
    return object_detail(request, queryset, object_id, extra_context=extra_context)

@login_required
def network_events(request, object_id):
    """Display events related to network"""
    network = Network.objects.get(pk=object_id)
    queryset = Network.objects.all()
    related_hosts = [nh.host.pk for nh in NetworkHost.objects.filter(network=network)]
    events = Event.objects.filter(source_host__pk__in=related_hosts)
    extra_context = {
        'events': events
    }
    return object_detail(request, queryset, object_id,
                         extra_context=extra_context,
                         template_name='networks/network_events.html')
