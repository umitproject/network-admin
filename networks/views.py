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
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.generic.create_update import *
from django.views.generic.list_detail import *
from django.views.generic.simple import direct_to_template, redirect_to
from django.shortcuts import get_object_or_404

from events.models import Event
from networks.models import Host, Network, NetworkHost
from networks.forms import *
from networks.utils import *

from search.core import search

@login_required
def host_list(request, page=None):
    
    host_queryset = filter_by_user(Host, request.user)
    
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
                          'search_results': search_results},
        'template_name': 'networks/host_list.html'
    }
    return object_list(request, page=page, **kwargs)

@login_required
def host_detail(request, object_id):
    
    host = get_object_or_404(Host, pk=object_id)
    
    if not user_has_access(host, request.user):
        return direct_to_template(request, "no_permissions.html")
    
    extra_context = {
        'can_edit': user_can_edit(host, request.user)
    }
    
    return object_detail(request, Host.objects.all(), object_id,
                         extra_context=extra_context)

@login_required
def host_create(request):
    
    if request.method == 'POST':
        form = HostCreateForm(request.POST)
        if form.is_valid():
            host = form.save()
            return redirect_to(request, url=host.get_absolute_url())
    
    extra_context = {
        'form': HostCreateForm(initial={'user': request.user.pk})
    }
    return direct_to_template(request, 'networks/host_form.html', extra_context)

@login_required
def host_update(request, object_id):
    
    host = get_object_or_404(Host, pk=object_id)
    
    if not user_can_edit(host, request.user):
        return direct_to_template(request, "no_permissions.html")
    
    return update_object(request, object_id=object_id, form_class=HostUpdateForm,
                         template_name='networks/host_update.html')

@login_required
def host_delete(request, object_id):
    
    host = get_object_or_404(Host, pk=object_id)
    
    if host.user != request.user:
        return direct_to_template(request, "no_permissions.html")
    
    return delete_object(request, object_id=object_id,
                         model=Host, post_delete_redirect=reverse('host_list'))

@login_required
def network_list(request):
    
    net_queryset = filter_by_user(Network, request.user)
    
    network_list_args = {
        'queryset': net_queryset,
        'paginate_by': 15,
        'extra_context': {'url': '/network/network/list/'}
    }
    return object_list(request, **network_list_args)

@login_required
def network_detail(request, object_id):
    """
    Network detail page has the following features:
        * displaying basic network info (name, description, etc.)
        * listing hosts related to network
        * creating relations between network and host
        * removing relations between network and host(s)
    """
    network = get_object_or_404(Network, pk=object_id)
    
    if not user_has_access(network, request.user):
        return direct_to_template(request, "no_permissions.html")
    
    edit = user_can_edit(network, request.user)
    
    # remove relation between the network and selected host(s)
    if request.POST.getlist('remove_host'):
        if edit:
            hosts_pk = request.POST.getlist('remove_host')
            network_host = NetworkHost.objects.filter(network=network, host__pk__in=hosts_pk)
            network_host.delete()
    
    # create relation between the network and selected host
    if request.POST.get('add_host'):
        if edit:
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
        'hosts_other': hosts_other,
        'can_edit': edit
    }
    return object_detail(request, queryset, object_id, extra_context=extra_context)

@login_required
def network_create(request):
    
    if request.method == 'POST':
        form = NetworkCreateForm(request.POST)
        if form.is_valid():
            network = form.save()
            return redirect_to(request, url=network.get_absolute_url())
    
    extra_context = {
        'form': NetworkCreateForm(initial={'user': request.user.pk})
    }
    return direct_to_template(request, 'networks/network_form.html', extra_context)

@login_required
def network_update(request, object_id):
    
    network = get_object_or_404(Network, pk=object_id)
    
    if not user_can_edit(network, request.user):
        return direct_to_template(request, "no_permissions.html")
    
    return update_object(request, object_id=object_id, form_class=NetworkUpdateForm,
                         template_name='networks/network_update.html')

@login_required
def network_delete(request, object_id):
    
    network = get_object_or_404(Network, pk=object_id)
    
    if network.user != request.user:
        return direct_to_template(request, "no_permissions.html")
    
    return delete_object(request, object_id=object_id,
                         model=Network, post_delete_redirect=reverse('network_list'))

@login_required
def network_events(request, object_id):
    """Display events related to network"""
    
    network = get_object_or_404(Network, pk=object_id)
    
    if not user_has_access(network, request.user):
        return direct_to_template(request, "no_permissions.html")
    
    edit = user_can_edit(network, request.user)

    queryset = Network.objects.all()
    related_hosts = [nh.host.pk for nh in NetworkHost.objects.filter(network=network)]
    events = Event.objects.filter(source_host__pk__in=related_hosts)
    extra_context = {
        'events': events,
        'can_edit': edit
    }
    return object_detail(request, queryset, object_id,
                         extra_context=extra_context,
                         template_name='networks/network_events.html')

@login_required
def share(request, object_type, object_id):
    model = Network if object_type == 'network' else Host
    obj = model.objects.get(pk=object_id)
    
    user_id = request.POST.get('share')
    if user_id:
        user = User.objects.get(pk=user_id)
        obj.share(user)
    
    return share_list(request, object_type, object_id)

@login_required
def share_not(request, object_type, object_id, user_id):
    model = Network if object_type == 'network' else Host
    obj = model.objects.get(pk=object_id)
        
    user = User.objects.get(pk=user_id)
    
    obj.share_not(user)
    
    return share_list(request, object_type, object_id)

@login_required
def share_edit(request, object_type, object_id, user_id):
    model = Network if object_type == 'network' else Host
    obj = model.objects.get(pk=object_id)
    
    user = User.objects.get(pk=user_id)
    
    obj.share_edit(user)
    
    return share_list(request, object_type, object_id)

@login_required
def share_list(request, object_type, object_id):
    model = Network if object_type == 'network' else Host
    obj = model.objects.get(pk=object_id)
    
    all_users = User.objects.all()
    other_users = []
    for user in all_users:
        if not obj.user_has_access(user):
            other_users.append(user)
    
    extra_context = {
        'object': obj,
        'object_type': object_type,
        'other_users': other_users
    }
    
    return direct_to_template(request, 'networks/share.html', extra_context)
