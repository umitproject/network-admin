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

import time
import datetime
import random

try:
    import simplejson as json
except ImportError:
    import json

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from netadmin.networks.models import Host
from netadmin.events.models import Event, EventType


class WebAPITest(TestCase):
    def setUp(self):
        self.username = 'user'
        self.password = 'pass'
        
        #set up Django user
        self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        
        #set up Django testing client
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        
        #set up events types
        for name in ['INFO', 'WARNING', 'CRITICAL', 'ERROR']:
            event_type = EventType(name=name, user=self.user,
                                   alert_level=1)
            event_type.save()
        
        #set up some hosts
        for i in xrange(10):
            h = Host(name='host_%i' % i,
                     description='description number %i' % i,
                     ipv4='127.0.0.%i' % (i+1),
                     ipv6='0:0:0:0:0:0:7f00:%i' % (i+1),
                     user=self.user)
            h.save()
            
        types = EventType.objects.all()
        hosts = Host.objects.all()
        for i in xrange(10):
            e = Event(message='event_%i' % i,
                short_message='short message #%i' % i,
                event_type=random.choice(types),
                protocol='SMTP',
                timestamp='%s' % str(datetime.datetime.now()),
                source_host = hosts[i],
                fields_class='Class%i' % i,
                fields_data=''
            )
            e.save()
    
    def test_hosts(self):
        """Get all hosts details
        """
        hosts = Host.objects.all()
        for host in hosts:
            response = self.client.get('/api/host/%i/' % host.pk)
            host_json = json.loads(response.content)
            self.assertIn('host_id', host_json.keys())
    
    def test_hosts_list(self):
        """Get hosts list
        """
        response = self.client.get('/api/host/list/')
        j = json.loads(response.content)
        
        self.assertIn('hosts', j.keys())

        hosts_list = j['hosts']
        for host in hosts_list:
            self.assertIn('id', host.keys())
            self.assertIn('name', host.keys())
            
            response = self.client.get('/api/host/%i/' % host['id'])
            j = json.loads(response.content)
            
            self.assertIn('host_id', j.keys())
        
    def test_report_event(self):
        """
        Report event for not existing host
        and check if that host has been added successfully
        """
        event = {
            'description': 'Message',
            'short_description': 'Short message',
            'event_type': 'INFO',
            'protocol': 'SMTP',
            'timestamp': '%s' % str(time.time()),
            'hostname': 'host_a',
            'source_host_ipv4': '1.2.3.4',
            'source_host_ipv6': '2002:0:0:0:0:0:102:304',
            'fields_class': 'ClassName',
            'fields_data': '',
        }
        
        response = self.client.post('/api/event/report/', data=event)
        r_json = json.loads(response.content)
        self.assertEqual(r_json['status'], 'ok')
        
        try:
            Host.objects.get(ipv4='1.2.3.4', ipv6='2002:0:0:0:0:0:102:304')
        except Host.DoesNotExist:
            self.assertTrue(False)
        
    def test_report_events(self):
        """Report set of events"""
        
        def gen_event(index):
            #types below come from Dragos' documentation for Network Inventory
            types = ['CRITICAL', 'WARNING', 'INFO', 'RECOVERY']
            event = {
                'description': 'event_%i' % index,
                'short_description': 'event short description %i' % index,
                'event_type': types[random.randint(0, len(types) - 1)],
                'protocol': 'SMTP',
                'timestamp': '%s' % str(time.time()),
                'source_host_ipv4': '127.0.0.%i' % (index + 1),
                'source_host_ipv6': '0:0:0:0:0:0:7f00:%i' % (index + 1),
                'fields_class': 'Class%i' % index,
                'fields_data': '',
            }
            return event
        
        events = [gen_event(i) for i in xrange(10)]
        
        events_json = json.dumps(events)
        
        response = self.client.post('/api/event/report/',
                                    data={'events': events_json})
        r_json = json.loads(response.content)
        self.assertEqual(r_json['status'], 'ok')
            
    def test_event_details(self):
        """Get all events details"""
        if not Event.objects.all():
            raise Exception
        for event in Event.objects.all():
            response = self.client.get('/api/event/%s/' % event.pk)
            j = json.loads(response.content)
            self.assertIn('event_id', j.keys())
            
    def test_events_list(self):
        """Get events list"""
        url = reverse('api_event_list')
        response = self.client.get(url)
        j = json.loads(response.content)
        self.assertIn('events', j.keys())
