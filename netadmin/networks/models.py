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
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext as _

from netadmin.permissions.models import ObjectPermission


class NetworkObject(models.Model):
    """
    Abstract model class for objects like host or network.
    Every object belongs to specified user
    """
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, blank=False, null=False)
    
    def __unicode__(self):
        return self.name
    
    def short_description(self, word_limit=15, char_limit=150):
        words = self.description.split()
        if len(words) > word_limit:
            return '%s...' % ' '.join(words[:word_limit])
        elif len(self.description) > char_limit:
            return '%s...' % self.description[:char_limit]
        else:
            return self.description
    
    def sharing_users(self):
        ct = ContentType.objects.get_for_model(self.__class__)
        perms = ObjectPermission.objects.filter(content_type=ct,
                                                object_id=self.pk)
        return [(perm.user, perm.edit) for perm in perms]
    
    def events(self):
        return self.event_set.all().order_by('-timestamp')
    
    def latest_event(self):
        events = self.events().order_by('-timestamp')
        return events[0] if events else None
    
    def api_list(self):
        return {
            'id': self.pk,
            'name': self.name
        }
    
    class Meta:
        abstract = True

class Host(NetworkObject):
    """The single host in the network
    """
    ipv4 = models.IPAddressField(verbose_name=_("IPv4 address"))
    time_zone = models.FloatField(verbose_name=_("Time Zone"),blank = True,null=True)
    ipv6 = models.CharField(max_length=39, verbose_name=_("IPv6 address"), 
                            blank=True, null=True)
    
    def __unicode__(self):
        return "Host '%s'" % self.name
                            
    @permalink
    def get_absolute_url(self):
        return ('host_detail', [str(self.pk)])
    
    def delete(self, *args, **kwargs):
        # delete all events related to this host
        events = self.events()
        events.delete()
        
        # delete network-host relations
        related = self.networkhost_set.all()
        related.delete()
        
        super(Host, self).delete(*args, **kwargs)
    
    def networks(self):
        nethost = self.networkhost_set.all().only('id')
        nets = [nh.network.pk for nh in nethost]
        return Network.objects.filter(pk__in=nets)
    
    def fields(self):
        from netadmin.events.models import EventFieldsNotValid
        fields_list = []
        for event in self.events():
            try:
                for field in event.fields.keys():
                    if field not in fields_list:
                        fields_list.append(field)
            except EventFieldsNotValid:
                pass
        return fields_list
    
    def in_network(self, network):
        try:
            nh = self.networkhost_set.get(network=network)
        except NetworkHost.DoesNotExist:
            return False
        return True
    
    def api_detail(self):
        return {
            'host_id': self.pk,
            'host_name': self.name,
            'host_description': self.description,
            'ipv4': self.ipv4,
            'ipv6': self.ipv6,
            'time_zone':self.time_zone
        }

class Network(NetworkObject):
    
    def __unicode__(self):
        return "Network '%s'" % self.name
    
    @permalink
    def get_absolute_url(self):
        return ('network_detail', [str(self.pk)])
    
    def delete(self, *args, **kwargs):
        related = NetworkHost.objects.filter(network=self)
        related.delete()
        super(Network, self).delete(*args, **kwargs)
    
    def hosts(self):
        """Returns all hosts in the network
        """
        related = self.networkhost_set.all()
        hosts_ids = [rel.host.pk for rel in related]
        return Host.objects.filter(pk__in=hosts_ids)
    
    def has_host(self, host):
        return True if host in self.hosts() else False
    
    def events(self):
        from netadmin.events.models import Event
        hosts = self.hosts()
        events = Event.objects.filter(source_host__in=list(hosts))
        return events.order_by('-timestamp')
    
    def api_detail(self):
        return {
            'network_id': self.pk,
            'network_name': self.name,
            'network_description': self.description
        }
    
class NetworkHost(models.Model):
    """
    Since one cannot use ManyToManyField type in GAE [1], we have to
    write extra model that will provide application with many-to-many
    relationship between networks and hosts.
    
    To ensure that after deleting host or network its relations will
    be removed too, we have to override delete() method for both
    Host and Network classes. Those methods should look like that:
    
    def delete(self, *args, **kwargs):
        related = Nself.networkhost_set.all()
        related.delete()
        super(Network, self).delete(*args, **kwargs)
        
    for Network class, and:
    
    def delete(self, *args, **kwargs):
        related = self.networkhost_set.all()
        related.delete()
        super(Host, self).delete(*args, **kwargs)
        
    for Host class. 
    
    [1] http://www.allbuttonspressed.com/projects/djangoappengine
    """
    network = models.ForeignKey(Network)
    host = models.ForeignKey(Host)

#class HostAdmin(admin.ModelAdmin):
#    list_display = ('name', 'ipv4', 'ipv6', 'user')
#admin.site.register(Host)
#
#class NetworkAdmin(admin.ModelAdmin):
#    list_display = ('name', 'user')
#admin.site.register(Network, NetworkAdmin)
#
#admin.site.register(NetworkHost)
