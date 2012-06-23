#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Amit Pal <amix.pal@gmail.com>
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

from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext as _
import datetime
from django.core.exceptions import ValidationError

from netadmin.permissions.utils import SharedObject
from utils import IPv6_validation, IPv4_validation



class NetworkObject(models.Model, SharedObject):
    """
    Abstract model class for objects like host or network.
    Every object belongs to specified user
    """
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, blank=False, null=False)
    subnet = models.BooleanField(default= False)
    
    def __unicode__(self):
        return self.name
    
    def short_description(self, word_limit=15):
        words = self.description.split()
        if len(words) > word_limit:
            return '%s...' % ' '.join(words[:word_limit])
        else:
            return self.description
    
    def events(self):
        return self.event_set.all().order_by('-timestamp')
    
    def latest_event(self):
        return self.event_set.latest('timestamp')
    
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
    timezone = models.CharField(max_length = 30, null=True, blank=True)
    ipv4 = models.CharField(max_length=39,verbose_name=_("IPv4 address"),
                            validators=[IPv4_validation])
    ipv6 = models.CharField(max_length=39, verbose_name=_("IPv6 address"), 
                            blank=True, validators=[IPv6_validation])

    @permalink
    def get_absolute_url(self):
       # import pdb;pdb.set_trace()
        return ('host_detail', [str(self.pk)])
    
    def delete(self, *args, **kwargs):
        #import pdb;pdb.set_trace()
        # delete all events related to this host
        # TODO
        # user should be asked if events should be deleted
        # or assigned to "dummy host"
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
        #import pdb;pdb.set_trace()
        return {
            'host_id': self.pk,
            'host_name': self.name,
            'host_description': self.description,
            'ipv4': self.ipv4,
            'ipv6': self.ipv6
        }

class Network(NetworkObject):
    
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

    def add_host(self, host):
        """Creates relation between host and network
        """
        try:
            self.networkhost_set.get(host=host)
        except NetworkHost.DoesNotExist:
            return NetworkHost.objects.create(network=self, host=host)

    def remove_host(self, host):
        """Removes relation between host and network
        """
        try:
            relation = self.networkhost_set.get(host=host)
        except NetworkHost.DoesNotExist:
            return
        relation.delete()
    
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

