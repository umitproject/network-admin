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

from netadmin.events.models import Event, EventType
from netadmin.networks.models import Host
from netadmin.permissions.utils import grant_access


class EventTest(TestCase):
    """Tests for hosts
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('user', 'user@something.com', 'userpassword')
        self.user.save()
        self.client.login(username='user', password='userpassword')
        
        self.source_host = Host(name='Host', ipv4='1.2.3.4', user=self.user)
        self.source_host.save()
        
        event_type = EventType(name='INFO', user=self.user)
        event_type.save()
        
        event_data = {
            'message': 'Message',
            'short_message': 'short message',
            'event_type': event_type,
            'timestamp': '%s' % str(datetime.datetime.now()),
            'source_host': self.source_host
        }
        self.event = Event(**event_data)
        self.event.save()
        
    def test_event_detail(self):
        """Get event's details
        """
        url = '/event/%i/' % self.event.pk
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_event_list(self):
        """Get events list
        """
        url = '/event/list/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_shared_event_detail(self):
        """
        Make Other User the owner of the source host and then:
        
            1. Make sure that User hasn't access to the event
            2. Share source host with User and check if he has access
               to the event.
        """
        other_user =  User.objects.create_user('other', 'other@something.com',
                                               'otherpassword')
        other_user.save()
        
        self.source_host.user = other_user
        self.source_host.save()
        
        url = '/event/%i/' % self.event.pk
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
        grant_access(self.source_host, self.user)
        
        url = '/event/%i/' % self.event.pk
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        self.source_host.user = self.user
        self.source_host.save()
