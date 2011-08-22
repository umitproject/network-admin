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

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from piston.models import Consumer, Token


class UserTest(TestCase):
    """Tests for users
    """
    
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@something.com',
            'userpassword')
        self.user.save()
        
        self.client = Client()
        self.client.login(username='user', password='userpassword')
        
        self.consumer = Consumer(name=self.user.username, status='accepted',
                                 user=self.user)
        self.consumer.generate_random_codes()
        self.consumer.save()
        
        self.token = Token(token_type=Token.ACCESS, timestamp=time.time(),
                              is_approved=True, user=self.user,
                              consumer=self.consumer)
        self.token.generate_random_codes()
        self.token.save()
        
    def test_user_profile(self):
        profile = self.user.get_profile()
        self.assertEqual(profile.in_search, True)
        self.assertEqual(profile.is_public, True)

    def test_private_profile(self):
        response = self.client.get('/user/profile/')
        self.assertEqual(response.status_code, 200)
        
    def test_my_public_profile(self):
        response = self.client.get('/user/public/%s/' % self.user.username)
        self.assertEqual(response.status_code, 200)
        
    def test_public_profile(self):
        another_user = User.objects.create_user('another_user',
            'another_user@something.com', 'userpassword')
        another_user.save()
        
        response = self.client.get('/user/public/%s/' % another_user.username)
        self.assertEqual(response.status_code, 200)
        
        profile = another_user.get_profile()
        profile.is_public = False
        profile.save()
        response = self.client.get('/user/public/%s/' % another_user.username)
        self.assertEqual(response.status_code, 403)
        
    def test_refresh_access_token(self):
        token_key = self.token.key
        token_secret = self.token.secret
        
        response = self.client.get('/user/refresh_access_token/')
        self.assertEqual(response.status_code, 200)
        
        token = Token.objects.get(user=self.user)
        
        self.assertNotEqual(token.key, token_key)
        self.assertNotEqual(token.secret, token_secret)
