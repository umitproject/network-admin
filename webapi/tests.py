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

import base64, time, datetime, random
import simplejson as json

from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from networks.models import Host
from events.models import Event, EventType
from piston.oauth import *
from piston.models import *

class WebAPITest(TestCase):
    def setUp(self):
        #set up Django testing client
        self.client = Client()
        
        self.username = 'user'
        self.password = 'pass'
        
        #set up Django user
        self.user = User(username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        
        #set up events types
        for name in ['INFO', 'WARNING', 'CRITICAL']:
            event_type = EventType(name=name)
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
                event_type=random.choice(types),
                timestamp='%s' % str(datetime.datetime.now()),
                source_host = hosts[i],
                monitoring_module='%i' % i,
                monitoring_module_fields=''
            )
            e.save()
            
    def get_auth_string(self):
        """Helper function - returns basic authentication string"""
        auth = '%s:%s' % (self.username, self.password)
        auth_string = 'Basic %s' % base64.encodestring(auth)
        auth_string = auth_string.strip()
        return auth_string
    
    def test_hosts(self):
        """Get all hosts details"""
        hosts = Host.objects.all()
        auth_string = self.get_auth_string()
        for host in hosts:
            response = self.client.get(reverse('api_host_detail', args=[host.pk]),
                                   HTTP_AUTHORIZATION=auth_string)
            host_json = json.loads(response.content)
            self.assertIn('host_id', host_json.keys())
    
    def test_hosts_list(self):
        """Get hosts list"""
        auth_string = self.get_auth_string()
        
        response = self.client.get(reverse('api_host_list'),
                                   HTTP_AUTHORIZATION=auth_string)
        
        j = json.loads(response.content)
        
        self.assertIn('hosts', j.keys())

        hosts_list = j['hosts']
        for host in hosts_list:
            self.assertIn('id', host.keys())
            self.assertIn('name', host.keys())
            
            url = reverse('api_host_detail', args=[host['id']])
            response = self.client.get(url, HTTP_AUTHORIZATION=auth_string)
            
            j = json.loads(response.content)
            
            self.assertIn('host_id', j.keys())
        
    def test_basic_auth(self):
        """Test basic authentication""" 
        host = Host.objects.all()[0]
        url = reverse('api_host_detail', args=[host.pk])
        
        auth_string = self.get_auth_string()
        
        response = self.client.get(url, HTTP_AUTHORIZATION=auth_string)
        
        self.assertEqual(response.status_code, 200)
        
    def test_report_event(self):
        """
        Report event for not existing host
        and check if that host has been added successfully
        """
        event = {
            'message': 'Message',
            'event_type': 'INFO',
            'timestamp': '%s' % str(time.time()),
            'source_host_ipv4': '1.2.3.4',
            'source_host_ipv6': '2002:0:0:0:0:0:102:304',
            'monitoring_module': '0',
            'monitoring_module_fields': '',
        }
        
        auth_string = self.get_auth_string()
        
        response = self.client.post(reverse('api_report_event'),
                                    data=event,
                                    HTTP_AUTHORIZATION=auth_string)
        r_json = json.loads(response.content)
        self.assertEqual(r_json['status'], 'ok')
        
        try:
            host = Host.objects.get(ipv4='1.2.3.4', ipv6='2002:0:0:0:0:0:102:304')
        except Host.DoesNotExist:
            self.assertTrue(False)
        
    def test_report_events(self):
        """Report set of events"""
        
        def gen_event(index):
            #types below come from Dragos' documentation for Network Inventory
            types = ['CRITICAL', 'WARNING', 'INFO', 'RECOVERY']
            event = {
                'message': 'event_%i' % index,
                'event_type': types[random.randint(0, len(types) - 1)],
                'timestamp': '%s' % str(datetime.datetime.now()),
                'source_host_ipv4': '127.0.0.%i' % (index + 1),
                'source_host_ipv6': '0:0:0:0:0:0:7f00:%i' % (index + 1),
                'monitoring_module': '%i' % index,
                'monitoring_module_fields': '',
            }
            return event
        
        events = [gen_event(i) for i in xrange(10)]
        
        events_json = json.dumps(events)
        auth_string = self.get_auth_string()
        
        response = self.client.post(reverse('api_report_event'),
                                    data={'events': events_json},
                                    HTTP_AUTHORIZATION=auth_string)
        print response.content
        r_json = json.loads(response.content)
        self.assertEqual(r_json['status'], 'ok')
            
    def test_event_details(self):
        """Get all events details"""
        for event in Event.objects.all():
            url = reverse('api_event_detail', args=[event.pk])
            auth_string = self.get_auth_string()
            response = self.client.get(url, HTTP_AUTHORIZATION=auth_string)
            print response.content
            j = json.loads(response.content)
            self.assertIn('event_id', j.keys())
            
    def test_events_list(self):
        """Get events list"""
        url = reverse('api_event_list')
        auth_string = self.get_auth_string()
        response = self.client.get(url, HTTP_AUTHORIZATION=auth_string)
        j = json.loads(response.content)
        self.assertIn('events', j.keys())
