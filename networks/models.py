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

from django.contrib import admin
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from dbindexer.api import register_index

class NetworkObject(models.Model):
    """
    Abstract model class for objects like host or network.
    Every object belongs to specified user
    """
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, blank=True, null=True)
    
    def __unicode__(self):
        return self.name
    
    def get_short_description(self):
        WORD_LIMIT = 15
        CHAR_LIMIT = 150
        words = self.description.split()
        if len(words) > WORD_LIMIT:
            return '%s...' % ' '.join(words[:WORD_LIMIT])
        elif len(self.description) > CHAR_LIMIT:
            return '%s...' % self.description[:CHAR_LIMIT]
        else:
            return self.description
    short_description = property(get_short_description)
    
    class Meta:
        abstract = True

class Host(NetworkObject):
    """The single host in the network"""
    ipv4 = models.IPAddressField(verbose_name=_("IPv4 address"))
    ipv6 = models.CharField(max_length=39, verbose_name=_("IPv6 address"), blank=True)
                            
    def get_absolute_url(self):
        return reverse('host_detail', args=[self.pk])
    
    def delete(self, *args, **kwargs):
        # delete all events related to this host
        from events.models import Event
        from networks.models import NetworkHost
        events = Event.objects.filter(source_host=self)
        events.delete()
        
        # delete network-host relations
        related = NetworkHost.objects.filter(host=self)
        related.delete()
        
        super(Host, self).delete(*args, **kwargs)
        
    def get_events(self):
        """Returns all events for the host"""
        from events.models import Event
        return Event.objects.filter(source_host=self)
    events = property(get_events)
    
    def has_events(self):
        if self.get_events().count():
            return True
        else:
            return False
        
    def _last_event(self):
        events = self.events.order_by('-timestamp')
        return events[0] if events else None
    last_event = property(_last_event)
    
    def in_network(self, network):
        try:
            h = NetworkHost.objects.get(network=network, host=self)
        except NetworkHost.DoesNotExist:
            return False
        return True
    
    def user_has_access(self, user):
        from networks.models import HostAccess
        if user == self.user:
            return True
        
        try:
            ac = HostAccess.objects.get(user=user, host=self)
        except HostAccess.DoesNotExist:
            return False
        
        return True
    
    def user_can_edit(self, user):
        from networks.models import HostAccess
        if user == self.user:
            return True
        
        try:
            ac = HostAccess.objects.get(user=user, host=self)
        except HostAccess.DoesNotExist:
            return False
        
        if ac.edit == True:
            return True
        else:
            return False
    
    def share(self, user):
        from networks.models import HostAccess
        if user == self.user:
            return None
        ac, created = HostAccess.objects.get_or_create(user=user, host=self)
        ac.shared_directly = True
        ac.save()
        return ac
    
    def share_not(self, user):
        from networks.models import HostAccess
        if user == self.user:
            return
        try:
            ac = HostAccess.objects.get(user=user, host=self)
        except HostAccess.DoesNotExist:
            return
        ac.delete()
        
    def share_edit(self, user):
        from networks.models import HostAccess
        if user == self.user:
            return
        
        try:
            ac = HostAccess.objects.get(user=user, host=self)
        except NetworkAccess.DoesNotExist:
            return
        
        ac.edit = False if ac.edit else True
        ac.save()
        
    def _sharing_users(self):
        from networks.models import HostAccess
        pks = [ac.user.pk for ac in HostAccess.objects.filter(host=self)]
        users = User.objects.filter(pk__in=pks)
        edit = [self.user_can_edit(user) for user in users]
        return zip(users, edit)
    sharing_users = property(_sharing_users)
        
    class Meta:
        permissions = (
            ("can_add", _("Can manually add a new host")),
            ("can_delete", _("Can delete host")),
            ("can_update", _("Can update basic host data like name or description")),
        )

class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'ipv4', 'ipv6', 'user')

admin.site.register(Host, HostAdmin)

class HostAccess(models.Model):
    user = models.ForeignKey(User)
    host = models.ForeignKey(Host)
    edit = models.BooleanField(default=True)
    # share_directly is set to True if host was shared not through network
    share_directly = models.BooleanField(default=False)
    
    def __unicode__(self):
        return 'Host %s owned by %s' % (self.host.name, self.user.username)
    
admin.site.register(HostAccess)

class Network(NetworkObject):
    
    def delete(self, *args, **kwargs):
        related = NetworkHost.objects.filter(network=self)
        related.delete()
        super(Network, self).delete(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('network_detail', args=[self.pk])
        
    def get_hosts_count(self):
        return NetworkHost.objects.filter(network=self).count()
    
    def get_hosts(self):
        """Returns all hosts in the network"""
        pks = [nh.host.pk for nh in NetworkHost.objects.filter(network=self)]
        return Host.objects.filter(pk__in=pks)
    hosts = property(get_hosts)
    
    def has_hosts(self):
        """Returns True if there is any host in the network"""
        return True if self.hosts else False
    
    def has_host(self, host):
        return True if host in self.hosts else False
    
    def get_events(self):
        """Returns events for all hosts in the network"""
        from events.models import Event
        hosts_ids = [host.pk for host in self.get_hosts()]
        return Event.objects.filter(source_host__pk__in=hosts_ids)
    events = property(get_events)
    
    def has_events(self):
        """Returns True if there are any events from host/network in the report"""
        return True if self.events else False
        
    def _last_event(self):
        events = self.events.order_by('-timestamp')
        return events[0] if events else None
    last_event = property(_last_event)
    
    def user_has_access(self, user):
        from networks.models import NetworkAccess
        if user == self.user:
            return True
        
        try:
            ac = NetworkAccess.objects.get(user=user, network=self)
        except NetworkAccess.DoesNotExist:
            return False
        
        return True
    
    def user_can_edit(self, user):
        from networks.models import NetworkAccess
        if user == self.user:
            return True
        
        try:
            ac = NetworkAccess.objects.get(user=user, network=self)
        except NetworkAccess.DoesNotExist:
            return False
        
        if ac.edit == True:
            return True
        else:
            return False
    
    def share(self, user):
        """Share the network with other user"""
        from networks.models import NetworkAccess
        if user == self.user:
            return None
        # share the network
        net_ac, created = NetworkAccess.objects.get_or_create(user=user, network=self)
        if created:
            # share hosts
            for host in self.hosts:
                ac, created = HostAccess.objects.get_or_create(user=user, host=host)
        return net_ac
    
    def share_not(self, user):
        from networks.models import NetworkAccess
        if user == self.user:
            return
        
        try:
            net_ac = NetworkAccess.objects.get(user=user, network=self)
        except NetworkAccess.DoesNotExist:
            return
        net_ac.delete()
        
        for host in self.hosts:
            host_ac = HostAccess.objects.get(user=user, host=host)
            
            if host_ac.share_directly:
                continue
            
            shared_nets = [na.network for na in NetworkAccess.objects.filter(user=user)]
            for net in shared_nets:
                if net.has_host(host):
                    break
            else:
                host_ac.delete()
                
    def share_edit(self, user):
        from networks.models import NetworkAccess
        if user == self.user:
            return
        
        try:
            ac = NetworkAccess.objects.get(user=user, network=self)
        except NetworkAccess.DoesNotExist:
            return
        
        ac.edit = False if ac.edit else True
        ac.save()
                
    def _sharing_users(self):
        from networks.models import NetworkAccess
        pks = [ac.user.pk for ac in NetworkAccess.objects.filter(network=self)]
        users = User.objects.filter(pk__in=pks)
        edit = [self.user_can_edit(user) for user in users]
        return zip(users, edit)
    sharing_users = property(_sharing_users)
        
    class Meta:
        permissions = (
            ("can_add", _("Can create networks")),
            ("can_update", _("Can update networks")),
            ("can_add_host", _("Can add host to network")),
            ("can_remove_host", _("Can remove host from network")),
        )

class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')

admin.site.register(Network, NetworkAdmin)

class NetworkAccess(models.Model):
    user = models.ForeignKey(User)
    network = models.ForeignKey(Network)
    edit = models.BooleanField(default=True)
    
    def __unicode__(self):
        return 'Network %s owned by %s' % (self.network.name, self.user.username)
    
admin.site.register(NetworkAccess)

class NetworkHost(models.Model):
    """
    Since one cannot use ManyToManyField type in GAE [1], we have to
    write extra model that will provide application with many-to-many
    relationship between networks and hosts.
    
    To ensure that after deleting host or network its relations will
    be removed too, we have to override delete() method for both
    Host and Network classes. Those methods should look like that:
    
    def delete(self, *args, **kwargs):
        related = NetworkHost.objects.filter(network=self)
        related.delete()
        super(Network, self).delete(*args, **kwargs)
        
    for Network class, and:
    
    def delete(self, *args, **kwargs):
        related = NetworkHost.objects.filter(host=self)
        related.delete()
        super(Host, self).delete(*args, **kwargs)
        
    for Host class. 
    
    [1] http://www.allbuttonspressed.com/projects/djangoappengine
    """
    network = models.ForeignKey(Network)
    host = models.ForeignKey(Host)

admin.site.register(NetworkHost)
