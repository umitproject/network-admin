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
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from networks.models import Host
from networks.forms import *
from networks.utils import *

class HostTest(TestCase):
    """Tests for hosts"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('user', 'user@something.com', 'userpassword')
        self.client.login(username='user', password='userpassword')
        self.host = Host(name='Host', description='Description', ipv4='1.2.3.4', ipv6='', user=self.user)
        
    def test_host_list(self):
        """Get hosts list"""
        for i in xrange(10):
            host = Host(name='Host %i' % i, description='Description',
                        ipv4='1.2.3.%i' % i, ipv6='', user=self.user)
            host.save()
        response = self.client.get(reverse('host_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_host_list_empty(self):
        """Get empty hosts list"""
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
        self.assertEqual(response.status_code, 301)
        
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
        
class NetworkTest(TestCase):
    """Tests for networks"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('user', 'user@something.com', 'userpassword')
        self.client.login(username='user', password='userpassword')
        
    def test_network_list(self):
        """Get networks list"""
        for i in xrange(10):
            network = Network(name='Network %i' % i,
                              description='Description %i' % i,
                              user=self.user)
            network.save()
        response = self.client.get(reverse('network_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_network_list_empty(self):
        """Get empty networks list"""
        response = self.client.get(reverse('network_list'))
        self.assertEqual(response.status_code, 200)
        
    def test_network_detail(self):
        """Get network details"""
        network = Network(name='Network', description='Description', user=self.user)
        network.save()
        response = self.client.get(reverse('network_detail', args=[network.pk]))
        self.assertEqual(response.status_code, 200)

    def test_network_create(self):
        """Creating new network"""
        network_data = {
            'name': 'New network',
            'description': 'New network description'
        }
        response = self.client.post(reverse('network_new'), network_data)
        self.assertEqual(response.status_code, 301)
        
    def test_network_delete(self):
        """Deleting existing network"""
        network = Network(name='Network', description='Description', user=self.user)
        network.save()
        response = self.client.post(reverse('network_delete', args=[network.pk]))
        self.assertEqual(response.status_code, 302)
        
    def test_network_update(self):
        """Update existing network"""
        network = Network(name='Network', description='Description', user=self.user)
        network.save()
        network_data = {
            'name': 'New name',
            'description': 'New description'
        }
        response = self.client.post(reverse('network_update', args=[network.pk]), network_data)
        self.assertEqual(response.status_code, 302)
        
class UserAccessTest(TestCase):
    """Tests for user access and sharing objects"""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user('user', 'user@something.com', 'userpassword')
        self.client.login(username='user', password='userpassword')
        
        self.other_user = User.objects.create_user('other', 'other@something.com', 'otherpassword')
        
        self.host = Host(name="Host", description="Description",
                         ipv4='1.2.3.4', ipv6='2002:0:0:0:0:0:c22:384e',
                         user=self.user)
        self.host.save()
        
        self.net = Network(name="Net", description="Description", user=self.user)
        self.net.save()
        
    def test_user_host_access(self):
        access = user_has_access(self.host, self.user)
        self.assertEqual(access, True)
        
        access = user_has_access(self.host, self.other_user)
        self.assertEqual(access, False)
        
    def test_user_host_share(self):
        self.host.share(self.other_user)
        access = user_has_access(self.host, self.other_user)
        self.assertEqual(access, True)
        
        access = user_can_edit(self.host, self.other_user)
        self.assertEqual(access, True)
        
        self.host.share_edit(self.other_user)
        access = user_can_edit(self.host, self.other_user)
        self.assertEqual(access, False)
        
        self.host.share_not(self.other_user)
        access = user_has_access(self.host, self.other_user)
        self.assertEqual(access, False)
        
    def test_user_network_access(self):
        access = user_has_access(self.net, self.user)
        self.assertEqual(access, True)
        
        access = user_has_access(self.net, self.other_user)
        self.assertEqual(access, False)
        
    def test_user_network_share(self):
        self.net.share(self.other_user)
        access = user_has_access(self.net, self.other_user)
        self.assertEqual(access, True)
        
        access = user_can_edit(self.net, self.other_user)
        self.assertEqual(access, True)
        
        self.net.share_edit(self.other_user)
        access = user_can_edit(self.net, self.other_user)
        self.assertEqual(access, False)
        
        self.net.share_not(self.other_user)
        access = user_has_access(self.net, self.other_user)
        self.assertEqual(access, False)
