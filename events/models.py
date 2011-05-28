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

import json
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib import admin
from networks.models import Host

class Event(models.Model):
    message = models.CharField(max_length=300)
    timestamp = models.DateTimeField()
    event_type = models.CharField(max_length=50, verbose_name=_("Type"))
    source_host = models.ForeignKey(Host)
    monitoring_module = models.IntegerField(null=True, blank=True)
    monitoring_module_fields = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return "<Event %s - host '%s' at [%s]>" % \
            (self.event_type, self.source_host.name, str(self.timestamp))

    def get_details(self):
        """Returns event details extracted from monitoring module fields"""
        fields = json.loads(self.monitoring_module_fields)
        return fields

admin.site.register(Event)    
