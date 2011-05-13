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
from networks.models import Host

class SimpleTest(TestCase):
    def setUp(self):
        self.c = Client()
        for i in xrange(10):
            h = Host(name='host_%i' % i,
                     description='description number %i' % i,
                     ipv4='127.0.0.%i' % (i+1),
                     ipv6='0:0:0:0:0:0:7f00:%i' % (i+1))
            h.save()
    
    def test_hosts_list(self):
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
