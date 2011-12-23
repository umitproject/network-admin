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

from django.contrib.auth.models import User
from django.test import TestCase

from netadmin.networks.models import Host
from utils import user_has_access, grant_access, revoke_access, \
    user_can_edit, grant_edit, revoke_edit

class ShareTest(TestCase):
    """Tests for class-based permissions system
    """
    def setUp(self):
        self.owner = self.create_user('owner', 'pass')
        self.friend = self.create_user('friend', 'pass')

        self.host = Host(name='Host', ipv4='1.2.3.4', user=self.owner)
        self.host.save()

    def create_user(self, username, password, email=None):
        """Creates and returns User object
        """
        if not email:
            email = '%s@something.com' % username
        user = User.objects.create_user(username, email, password)
        user.save()
        return user

    def test_has_access(self):
        """By default only the owner should has an access to the object
        """
        self.assertEqual(self.host.has_access(self.owner), True)
        self.assertEqual(self.host.has_access(self.friend), False)

    def test_share(self):
        """The share() method grants user an access to the object
        """
        self.assertEqual(self.host.has_access(self.friend), False)

        self.host.share(self.friend)
        self.assertEqual(self.host.has_access(self.friend), True)

    def test_revoke(self):
        """The revoke() method revokes user an access to the object
        """
        self.host.share(self.friend)
        self.assertEqual(self.host.has_access(self.friend), True)

        self.host.revoke(self.friend)
        self.assertEqual(self.host.has_access(self.friend), False)

    def test_can_edit(self):
        """
        The can_edit() method should return True if user has permission
        to edit the object; otherwise it should return False
        """
        self.assertEqual(self.host.can_edit(self.owner), True)
        self.assertEqual(self.host.can_edit(self.friend), False)

    def test_grant_edit(self):
        """
        The share() method grants permission to edit if the 'edit'
        parameter was set to True
        """
        self.host.share(self.friend)
        self.assertEqual(self.host.can_edit(self.friend), False)

        self.host.share(self.friend, edit=True)
        self.assertEqual(self.host.can_edit(self.friend), True)

    def test_revoke_edit(self):
        """
        The share() method revokes permission to edit if the 'edit'
        parameter was set to False
        """
        self.host.share(self.friend, edit=True)
        self.assertEqual(self.host.can_edit(self.friend), True)

        self.host.share(self.friend, edit=False)
        self.assertEqual(self.host.can_edit(self.friend), False)

    def test_shared_objects(self):
        """
        The shared_objects() method should return list of objects
        owned or shared by the user
        """
        self.assertIn(self.host, Host.shared_objects(self.owner))
        self.assertNotIn(self.host, Host.shared_objects(self.friend))

        self.host.share(self.friend)
        self.assertIn(self.host, Host.shared_objects(self.friend))

class PermissionsTest(TestCase):
    """Tests for permissions system
    """
    
    def setUp(self):
        self.user_a = User.objects.create_user('user_a', 'user_a@something.com', 'userpassword')
        self.user_a.save()
        
        self.user_b = User.objects.create_user('user_b', 'user_b@something.com', 'userpassword')
        self.user_b.save()
        
        self.host = Host(name='Host', ipv4='1.2.3.4', user=self.user_a)
        self.host.save()
        
    def test_user_access(self):
        access = user_has_access(self.host, self.user_a)
        self.assertEqual(access, True)
        
        access = user_has_access(self.host, self.user_b)
        self.assertEqual(access, False)
        
    def test_grant_access(self):
        access = user_has_access(self.host, self.user_b)
        self.assertEqual(access, False)
        
        grant_access(self.host, self.user_b)
        access = user_has_access(self.host, self.user_b)
        self.assertEqual(access, True)
        
    def test_revoke_access(self):
        grant_access(self.host, self.user_b)
        access = user_has_access(self.host, self.user_b)
        self.assertEqual(access, True)
        
        revoke_access(self.host, self.user_b)
        access = user_has_access(self.host, self.user_b)
        self.assertEqual(access, False)
        
    def test_can_edit(self):
        edit = user_can_edit(self.host, self.user_a)
        self.assertEqual(edit, True)
        
        revoke_access(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, False)
        
        grant_access(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, True)
        
    def test_revoke_edit(self):
        grant_access(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, True)
        
        revoke_edit(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, False)
        
        revoke_access(self.host, self.user_b)
        
    def test_grant_edit(self):
        grant_access(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, True)
        
        revoke_edit(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, False)
        
        grant_edit(self.host, self.user_b)
        edit = user_can_edit(self.host, self.user_b)
        self.assertEqual(edit, True)
