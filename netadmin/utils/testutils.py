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

try:
    import simplejson as json
except ImportError:
    import json

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from netadmin.events.models import Event, EventType
from netadmin.networks.models import Host, Network


class BaseTest(TestCase):
    """Base class for every test case in Network Administrator
    """
    def setUp(self):
        self.client = Client()
        self.user = self.create_user('user', 'userpassword')
        self.user.save()
        self.client.login(username='user', password='userpassword')

    def create_user(self, username, password, email=None):
        if not email:
            email = '%s@something.com' % username
        user = User.objects.create_user(username, email, password)
        user.save()
        return user

class EventBaseTest(BaseTest):
    """Base class for every test case which needs to create events
    """
    def create_event(self, source_host, event_type, message="Message",
                     short_message=None, fields_data=None):
        if not short_message:
            short_message = message.lower()
        event_data = {
            'message': message,
            'short_message': short_message,
            'event_type': event_type,
            'timestamp': '%s' % str(datetime.datetime.now()),
            'source_host': source_host,
            'fields_data': fields_data and json.dumps(fields_data)
        }
        event = Event.objects.create(**event_data)
        return event

    def create_eventtype(self, name):
        event_type = EventType.objects.create(name=name, user=self.user)
        return event_type

class HostBaseTest(BaseTest):
    """Base class for every test case which needs to create hosts
    """
    def create_host(self, user, name, ipv4, ipv6='', description=""):
        host = Host.objects.create(name=name, description=description,
                                   ipv4=ipv4, ipv6=ipv6, user=user)
        return host

class NetworkBaseTest(BaseTest):
    """Base class for test cases that use Network model
    """
    def create_network(self, user, name, description=''):
        net = Network.objects.create(name=name, description=description,
                                     user=user)
        return net