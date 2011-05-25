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

from django.db import models
from django.utils.translation import ugettext as _

class Host(models.Model):
    """The single host in the network"""
    name = models.CharField(max_length=250)
    description = models.TextField()
    ipv4 = models.IPAddressField(verbose_name=_("IPv4 address"))
    ipv6 = models.IPAddressField(verbose_name=_("IPv6 address"))
    
class Network(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()