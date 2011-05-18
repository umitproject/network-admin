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

class Event(models.Model):
    message = models.CharField(max_length=300)
    timestamp = models.DateTimeField()
    type = models.CharField(max_length=50)
    source_host_ipv4 = models.IPAddressField(verbose_name=_("IPv4 address"))
    source_host_ipv6 = models.IPAddressField(verbose_name=_("IPv6 address"))
    monitoring_module = models.IntegerField()
    monitoring_module_fields = models.TextField()

    def get_details(self):
        """Returns event details extracted from monitoring module fields"""
        fields = json.loads(self.monitoring_module_fields)
        return fields

admin.site.register(Event)    
