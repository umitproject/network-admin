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
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from networks.models import Host
from piston.oauth import *
from piston.models import *

class SimpleTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.client = Client()
        self.user = User(username='user', password='pass')
        self.user.save()
        self.consumer = Consumer(
            name='consumer',
            description='lorem ipsum',
            key='1234',
            secret='abcd',
            status='accepted',
            user=self.user)
        self.consumer.save()
        for i in xrange(10):
            h = Host(name='host_%i' % i,
                     description='description number %i' % i,
                     ipv4='127.0.0.%i' % (i+1),
                     ipv6='0:0:0:0:0:0:7f00:%i' % (i+1))
            h.save()
        self.log = open('/home/piotrek/dev/projekty/network-admin/log.txt', 'w')
            
    def test_hosts(self):
        return
        """Select all hosts from database and get details of each """
        hosts = Host.objects.all()
        for host in hosts:
            response = self.client.get(reverse('host_detail', args=[host.pk]))
            host_json = json.loads(response.content)
            self.assertIn('host_id', host_json.keys())
    
    def test_hosts_list(self):
        return
        r = self.c.get('/api/host/list/')
        j = json.loads(r.content)
        
        self.assertIn('hosts', j.keys())

        hosts_list = j['hosts']
        for host in hosts_list:
            self.assertIn('id', host.keys())
            self.assertIn('name', host.keys())
            r = self.c.get('/api/host/%s/' % host['id'])
            j = json.loads(r.content)
            
            self.assertIn('host_id', j.keys())

    def test_oauth(self):
        """Test request authentication with OAuth"""
        host = Host.objects.all()[0]
        url = '/api/host/1/'
        consumer = Consumer.objects.all()[0]
        oaconsumer = OAuthConsumer(consumer.key, consumer.secret)
        request = OAuthRequest.from_consumer_and_token(oaconsumer, http_url=url)
        signature_method = OAuthSignatureMethod_HMAC_SHA1()
        request.sign_request(signature_method, oaconsumer, consumer)
        request.set_parameter('oauth_token', consumer.secret)
        response = self.client.get(url, request.parameters)
        self.log.write(str(request.parameters))
        self.log.write(response.content)
