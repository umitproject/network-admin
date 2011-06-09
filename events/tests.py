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

import datetime
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from events.models import Event, EventType
from networks.models import Host

class EventTest(TestCase):
    """Tests for hosts"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('user', 'user@something.com', 'userpassword')
        self.client.login(username='user', password='userpassword')
        
    def test_event_detail(self):
        """Create event and get event's details"""
        
        host = Host(name='Host', ipv4='1.2.3.4')
        host.save()
        
        event_type = EventType(name='INFO')
        event_type.save()
        
        event_data = {
            'message': 'Message',
            'event_type': event_type,
            'timestamp': '%s' % str(datetime.datetime.now()),
            'source_host': host
        }
        event = Event(**event_data)
        event.save()
        
        url = reverse('event_detail', args=[event.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_event_list(self):
        """Get events list"""
        url = reverse('event_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
