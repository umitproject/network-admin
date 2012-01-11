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

from django.core.paginator import Page
from django.core.urlresolvers import reverse
from django.test import TestCase

from models import Host, Network
from netadmin.permissions.utils import user_has_access, user_can_edit, \
    grant_access, revoke_access, revoke_edit
from netadmin.utils.testutils import EventBaseTest, HostBaseTest

class HostTest(HostBaseTest, EventBaseTest):
    def setUp(self):
        super(HostTest, self).setUp()
        self.host = self.create_host(self.user, "Host", '1.2.3.4')

    def test_short_description(self):
        """
        The short_description() method should return description shortened
        to specified number of words. By default, a short description should
        not be longer than 15 words
        """
        description = "Lorem ipsum dolor sit amet, consectetur adipiscing " \
            "elit. Sed quis est eros, vel luctus tortor. Pellentesque urna " \
            "dolor, lacinia a."

        self.host.description = description
        self.host.save()

        short = "Lorem ipsum dolor sit amet, consectetur adipiscing " \
            "elit. Sed quis est eros, vel luctus tortor...."
        self.assertEqual(self.host.short_description(), short)

        short = "Lorem ipsum dolor sit amet,..."
        self.assertEqual(self.host.short_description(word_limit=5), short)

    def test_unicode(self):
        """The __unicode__() method should return host name
        """
        self.assertEqual(self.host.__unicode__(), "Host")

    def test_get_absolute_url(self):
        """The absolute URL should be created using object's ID
        """
        url = reverse('host_detail', args=[self.host.pk])
        self.assertEqual(self.host.get_absolute_url(), url)

    def test_events(self):
        """
        The events() method should return list of events related to the host
        """
        h = self.create_host(self.user, "Host", '4.3.2.1')
        et = self.create_eventtype('INFO')
        event_a = self.create_event(self.host, et)
        event_b = self.create_event(h, et)

        self.assertIn(event_a, self.host.events())
        self.assertNotIn(event_b, self.host.events())

    def test_latest_event(self):
        """
        The latest_event() method should return the most recent event related
        to the host
        """
        et = self.create_eventtype('INFO')

        oldest = self.create_event(self.host, et)
        latest = self.create_event(self.host, et)

        self.assertEqual(self.host.latest_event(), latest)

    def test_fields(self):
        """
        The fields() method should return list of fields' names
        from all events reported to the host
        """
        et = self.create_eventtype('INFO')
        other_host = self.create_host(self.user, 'Other host', '1.1.1.1')

        # let's create some events that should be reported to the self.host
        self.create_event(self.host, et, fields_data={'a': 1, 'b': 2})
        self.create_event(self.host, et, fields_data={'c': 3})

        # the following event shouldn't be reported to the self.host
        self.create_event(other_host, et, fields_data={'d': 4})

        self.assertItemsEqual(self.host.fields(), [u'a', u'b', u'c'])
        self.assertItemsEqual(other_host.fields(), [u'd'])

    def test_object_detail(self):
        """
        The context on the host detail page should contain the following
        variables:

            * object - the host object
            * can_edit - True if user can edit the host, otherwise False
        """
        response = self.client.get(reverse('host_detail',
                                           args=[self.host.pk]))
        self.assertEqual(response.status_code, 200)

        self.assertIn('object', response.context)
        self.assertEqual(response.context['object'], self.host)

        self.assertIn('can_edit', response.context)

    def test_object_list(self):
        """
        The context on the host list page should contain the following
        variables:

            * hosts - a single page with a list of hosts
            * url - URL of the host list page

        Objects should be paginated by 10 elements per page
        """
        hosts = [self.create_host(self.user, 'host %i' % i, '1.1.1.%i' % i)
                 for i in xrange(10)]
        hosts = [self.host] + hosts

        response = self.client.get(reverse('host_list'))
        self.assertEqual(response.status_code, 200)

        print response.context['hosts']
        self.assertIn('hosts', response.context)
        self.assertIsInstance(response.context['hosts'], Page)
        self.assertItemsEqual(hosts[:10], response.context['hosts'].object_list)

        self.assertIn('url', response.context)
        self.assertEqual(response.context['url'], reverse('host_list'))

    def test_object_create(self):
        """After updating a host, a user should be redirected with 301
        """
        host_data = {
            'name': 'New host',
            'description': 'New host description',
            'ipv4': '12.34.56.78',
            'ipv6': '2002:0:0:0:0:0:c22:384e',
            'user': self.user.pk
        }
        response = self.client.post(reverse('host_new'), host_data)
        self.assertEqual(response.status_code, 301)

        host = Host.objects.all().order_by('-id')[0]
        self.assertEqual(host.name, host_data['name'])
        self.assertEqual(host.description, host_data['description'])
        self.assertEqual(host.ipv4, host_data['ipv4'])
        self.assertEqual(host.ipv6, host_data['ipv6'])
        self.assertEqual(host.user.pk, host_data['user'])

    def test_object_delete(self):
        """After deleting a host, a user should be redirected with 302
        """
        response = self.client.post(reverse('host_delete',
                                            args=[self.host.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.host, Host.objects.all())

    def test_object_update(self):
        """After updating a host, a user should be redirected with 302
        """
        host_data = {
            'name': 'New name',
            'description': 'New description'
        }
        self.assertNotEqual(self.host.name, host_data['name'])
        self.assertNotEqual(self.host.description, host_data['description'])

        url = reverse('host_update', args=[self.host.pk])
        response = self.client.post(url, host_data)
        self.assertEqual(response.status_code, 302)
        
        host = Host.objects.get(pk=self.host.pk)
        self.assertEqual(host.name, host_data['name'])
        self.assertEqual(host.description, host_data['description'])

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
            'description': 'New network description',
            'user': self.user.pk
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
        grant_access(self.host, self.other_user)
        access = user_has_access(self.host, self.other_user)
        self.assertEqual(access, True)
        
        access = user_can_edit(self.host, self.other_user)
        self.assertEqual(access, True)
        
        revoke_edit(self.host, self.other_user)
        access = user_can_edit(self.host, self.other_user)
        self.assertEqual(access, False)
        
        revoke_access(self.host, self.other_user)
        access = user_has_access(self.host, self.other_user)
        self.assertEqual(access, False)
        
    def test_user_network_access(self):
        access = user_has_access(self.net, self.user)
        self.assertEqual(access, True)
        
        access = user_has_access(self.net, self.other_user)
        self.assertEqual(access, False)
        
    def test_user_network_share(self):
        grant_access(self.net, self.other_user)
        access = user_has_access(self.net, self.other_user)
        self.assertEqual(access, True)
        
        access = user_can_edit(self.net, self.other_user)
        self.assertEqual(access, True)
        
        revoke_edit(self.net, self.other_user)
        access = user_can_edit(self.net, self.other_user)
        self.assertEqual(access, False)
        
        revoke_access(self.net, self.other_user)
        access = user_has_access(self.net, self.other_user)
        self.assertEqual(access, False)
