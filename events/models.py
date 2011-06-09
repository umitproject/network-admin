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

import simplejson as json
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib import admin
from networks.models import Host

class EventType(models.Model):
    """A very simple model written to make managing events types easier"""
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        from reports.models import ReportMetaEventType
        
        # delete relations between event type and reports
        related = ReportMetaEventType.objects.filter(event_type=self)
        related.delete()
        
        super(EventType, self).delete(*args, **kwargs)
        
admin.site.register(EventType)

class Event(models.Model):
    message = models.CharField(max_length=300)
    timestamp = models.DateTimeField()
    event_type = models.ForeignKey(EventType)
    source_host = models.ForeignKey(Host)
    monitoring_module = models.IntegerField(null=True, blank=True)
    monitoring_module_fields = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.message

    def get_details(self):
        """Returns event details extracted from monitoring module fields"""
        fields = json.loads(self.monitoring_module_fields)
        return fields

admin.site.register(Event)
