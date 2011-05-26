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

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from networks.models import Host
from networks.forms import *

class HostTest(TestCase):
    """Tests for hosts"""
    
    def setUp(self):
        self.client = Client()
        self.host = Host(name='Host', description='Description', ipv4='1.2.3.4', ipv6='')
        
    def test_host_list(self):
        """Get hosts list"""
        response = self.client.get(reverse('host_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_host_detail(self):
        """Get host details"""
        host = self.host
        host.save()
        response = self.client.get(reverse('host_detail', args=[host.pk]))
        self.assertEqual(response.status_code, 200)

    def test_host_create(self):
        """Creating new host"""
        host_data = {
            'name': 'New host',
            'description': 'New host description',
            'ipv4': '12.34.56.78',
            'ipv6': '2002:0:0:0:0:0:c22:384e'
        }
        response = self.client.post(reverse('host_new'), host_data)
        self.assertEqual(response.status_code, 302)
        
    def test_host_delete(self):
        """Deleting existing host"""
        host = self.host
        host.save()
        response = self.client.post(reverse('host_delete', args=[host.pk]))
        self.assertEqual(response.status_code, 302)
        
    def test_host_update(self):
        """Update existing host"""
        host = self.host
        host.save()
        host_data = {
            'name': 'New name',
            'description': 'New description'
        }
        response = self.client.post(reverse('host_update', args=[host.pk]), host_data)
        self.assertEqual(response.status_code, 302)
        
