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
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.client import Client
from reportmeta.models import ReportMeta, ReportMetaEventType
from networks.models import Network, Host, NetworkHost

class ReportMetaTest(TestCase):
    """Tests for reports meta"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('user', 'user@something.com', 'userpassword')
        self.client.login(username='user', password='userpassword')
        
        self.host = Host(name='Host', description='Description',
                         ipv4='1.2.3.4', ipv6='', user=self.user)
        self.host.save()
        
        self.network = Network(name='Network', description='Description',
                               user=self.user)
        self.network.save()
        
        self.net_host = NetworkHost(network=self.network, host=self.host)
        self.net_host.save()
        
    def test_reportmeta_host_list(self):
        for i in xrange(10):
            report_meta = ReportMeta(name='report %i' % i, description='description', period=7,
                                     object_type=ContentType.objects.get_for_model(Host),
                                     object_id=self.host.pk, user=self.user)
            report_meta.save()
        response = self.client.get(reverse('reportmeta_list', args=['host']))
        self.assertEqual(response.status_code, 200)
        
    def test_reportmeta_network_list(self):
        for i in xrange(10):
            report_meta = ReportMeta(name='report %i' % i, description='description', period=7,
                                     object_type=ContentType.objects.get_for_model(Network),
                                     object_id=self.network.pk, user=self.user)
            report_meta.save()
        response = self.client.get(reverse('reportmeta_list', args=['network']))
        self.assertEqual(response.status_code, 200)
    
    def test_reportmeta_detail(self):
        report_meta = ReportMeta(name='host report', description='description', period=7,
                                 object_type=ContentType.objects.get_for_model(Host),
                                 object_id=self.host.pk, user=self.user)
        report_meta.save()
        response = self.client.get(reverse('reportmeta_detail', args=[report_meta.pk]))
        self.assertEqual(response.status_code, 200)
        
        report_meta = ReportMeta(name='network report', description='description', period=7,
                                 object_type=ContentType.objects.get_for_model(Network),
                                 object_id=self.network.pk, user=self.user)
        report_meta.save()
        response = self.client.get(reverse('reportmeta_detail', args=[report_meta.pk]))
        self.assertEqual(response.status_code, 200)
    
    def test_reportmeta_create(self):
        reportmeta_host_data = {
            'name': 'New host report',
            'description': 'New host report description',
            'period': 1,
            'object_type': ContentType.objects.get_for_model(Host).pk,
            'object_id': self.host.pk,
            'user': self.user.pk
        }
        
        reportmeta_network_data = {
            'name': 'New network report',
            'description': 'New network report description',
            'period': 31,
            'object_type': ContentType.objects.get_for_model(Network).pk,
            'object_id': self.network.pk,
            'user': self.user.pk
        }
        
        response = self.client.post(reverse('reportmeta_new', args=['host']), reportmeta_host_data)
        self.assertEqual(response.status_code, 302)
        
        response = self.client.post(reverse('reportmeta_new', args=['network']), reportmeta_network_data)
        self.assertEqual(response.status_code, 302)
    
    def test_reportmeta_update(self):
        reportmeta_host = ReportMeta(name='host report', description='description', period=7,
                                 object_type=ContentType.objects.get_for_model(Host),
                                 object_id=self.host.pk, user=self.user)
        reportmeta_host.save()
        
        reportmeta_net = ReportMeta(name='network report', description='description', period=7,
                                 object_type=ContentType.objects.get_for_model(Network),
                                 object_id=self.network.pk, user=self.user)
        reportmeta_net.save()
        
        reportmeta_host_data = {
            'name': 'Updated host report',
            'description': 'Updated host report description',
            'period': 1,
            'object_type': ContentType.objects.get_for_model(Host).pk,
            'object_id': self.host.pk,
            'user': self.user.pk
        }
        
        reportmeta_network_data = {
            'name': 'Updated network report',
            'description': 'Updated network report description',
            'period': 31,
            'object_type': ContentType.objects.get_for_model(Network).pk,
            'object_id': self.network.pk,
            'user': self.user.pk
        }
        
        response = self.client.post(reverse('reportmeta_update', args=[reportmeta_host.pk]), reportmeta_host_data)
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('reportmeta_update', args=[reportmeta_net.pk]), reportmeta_network_data)
        self.assertEqual(response.status_code, 302)
    
    def test_reportmeta_delete(self):
        reportmeta_host = ReportMeta(name='host report', description='description', period=7,
                                 object_type=ContentType.objects.get_for_model(Host),
                                 object_id=self.host.pk, user=self.user)
        reportmeta_host.save()
        
        reportmeta_net = ReportMeta(name='network report', description='description', period=7,
                                 object_type=ContentType.objects.get_for_model(Network),
                                 object_id=self.network.pk, user=self.user)
        reportmeta_net.save()
        
        response = self.client.post(reverse('reportmeta_delete', args=[reportmeta_host.pk]))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('reportmeta_delete', args=[reportmeta_net.pk]))
        self.assertEqual(response.status_code, 302)
