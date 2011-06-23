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
        
    class Meta:
        permissions = (
            ("can_add", _("Can manually add a new host")),
            ("can_delete", _("Can delete host")),
            ("can_update", _("Can update basic host data like name or description")),
        )

admin.site.register(Host)
    
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
        return [net_host.host for net_host in NetworkHost.objects.filter(network=self)]
    hosts = property(get_hosts)
    
    def has_hosts(self):
        """Returns True if there is any host in the network"""
        return True if self.hosts else False
    
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
        
    class Meta:
        permissions = (
            ("can_add", _("Can create networks")),
            ("can_update", _("Can update networks")),
            ("can_add_host", _("Can add host to network")),
            ("can_remove_host", _("Can remove host from network")),
        )
    
admin.site.register(Network)

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
