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

import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.views.generic.create_update import create_object, update_object, \
    delete_object
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template, redirect_to
from django.http import Http404
from search.core import search

from netadmin.events.models import Event
from netadmin.networks.models import Host, Network, NetworkHost
from netadmin.networks.forms import HostCreateForm, HostUpdateForm, \
    NetworkCreateForm, NetworkUpdateForm
from netadmin.permissions.utils import filter_user_objects, \
    get_object_or_forbidden, grant_access, grant_edit, revoke_access, \
    revoke_edit, user_has_access


@login_required
def host_list(request, page=None):
    search_phrase = request.GET.get('s')
    if search_phrase:
        hosts = search(Host, search_phrase)
    else:
        hosts = filter_user_objects(request.user, Host)

    extra_context = {
        'hosts': hosts,
        'url': reverse('host_list')
    }
    return direct_to_template(request, 'networks/host_list.html',
                              extra_context=extra_context)

@login_required
def host_detail(request, object_id):
    
    host, edit = get_object_or_forbidden(Host, object_id, request.user)
    
    extra_context = {
        'can_edit': edit
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
    
    host, edit = get_object_or_forbidden(Host, object_id, request.user)
    
    if not edit:
        raise Http404()
    
    return update_object(request, object_id=object_id,
                         form_class=HostUpdateForm,
                         template_name='networks/host_update.html')

@login_required
def host_delete(request, object_id):
    
    host, edit = get_object_or_forbidden(Host, object_id, request.user)
    
    if host.user != request.user:
        raise Http404()
    
    return delete_object(request, object_id=object_id, model=Host,
                         post_delete_redirect=reverse('host_list'))

@login_required
def network_list(request):
    
    search_phrase = request.GET.get('s')
    if search_phrase:
        nets = search(Network, search_phrase)
    else:
        nets = filter_user_objects(request.user, Network)
    
    extra_context = {
        'networks': nets,
        'url': '/network/network/list/'
    }
    return direct_to_template(request, 'networks/network_list.html',
                              extra_context=extra_context)

@login_required
def network_detail(request, object_id):
    """
    Network detail page has the following features:
        * displaying basic network info (name, description, etc.)
        * listing hosts related to network
        * creating relations between network and host
        * removing relations between network and host(s)
    """
    network, edit = get_object_or_forbidden(Network, object_id, request.user)
    
    # remove relation between the network and selected host(s)
    if request.POST.getlist('remove_host'):
        if edit:
            hosts_pk = request.POST.getlist('remove_host')
            network_host = NetworkHost.objects.filter(network=network,
                                                      host__pk__in=hosts_pk)
            network_host.delete()
    
    # create relation between the network and selected host
    if request.POST.get('add_host'):
        if edit:
            host = Host.objects.get(pk=request.POST.get('add_host'))
            network_host = NetworkHost(network=network, host=host)
            network_host.save()
    
    queryset = Network.objects.all()
    if network.hosts:
        hosts_ids = [host.pk for host in network.hosts]
        hosts_other = Host.objects.exclude(pk__in=hosts_ids)
    else:
        hosts_other = Host.objects.all()
    extra_context = {
        'hosts_other': hosts_other,
        'can_edit': edit
    }
    return object_detail(request, queryset, object_id,
                         extra_context=extra_context)

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
    return direct_to_template(request, 'networks/network_form.html',
                              extra_context)

@login_required
def network_update(request, object_id):
    
    network, edit = get_object_or_forbidden(Network, object_id, request.user)
    
    if not edit:
        raise Http404()
    
    return update_object(request, object_id=object_id,
                         form_class=NetworkUpdateForm,
                         template_name='networks/network_update.html')

@login_required
def network_delete(request, object_id):
    
    network, edit = get_object_or_forbidden(Network, object_id, request.user)
    
    if network.user != request.user:
        raise Http404()
    
    return delete_object(request, object_id=object_id, model=Network,
                         post_delete_redirect=reverse('network_list'))

@login_required
def network_events(request, object_id):
    """Display events related to network"""
    
    network, edit = get_object_or_forbidden(Network, object_id, request.user)

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
    obj, edit = get_object_or_forbidden(model, object_id, request.user)
    user_id = request.POST.get('share')
    if user_id:
        user = User.objects.get(pk=user_id)
        grant_access(obj, user)
    return share_list(request, object_type, object_id)

@login_required
def share_not(request, object_type, object_id, user_id):
    model = Network if object_type == 'network' else Host
    obj, edit = get_object_or_forbidden(model, object_id, request.user)
    user = User.objects.get(pk=user_id)
    revoke_access(obj, user)
    return share_list(request, object_type, object_id)

@login_required
def share_edit(request, object_type, object_id, user_id):
    model = Network if object_type == 'network' else Host
    obj, edit = get_object_or_forbidden(model, object_id, request.user)
    user = User.objects.get(pk=user_id)
    if edit:
        revoke_edit(obj, user)
    else:
        grant_edit(obj, user)
    return share_list(request, object_type, object_id)

@login_required
def share_list(request, object_type, object_id):
    model = Network if object_type == 'network' else Host
    obj, edit = get_object_or_forbidden(model, object_id, request.user)
    all_users = User.objects.exclude(pk=request.user.pk)
    other_users = []
    for user in all_users:
        if not user_has_access(obj, user):
            other_users.append(user)
    extra_context = {
        'object': obj,
        'object_type': object_type,
        'other_users': other_users
    }
    return direct_to_template(request, 'networks/share.html', extra_context)
