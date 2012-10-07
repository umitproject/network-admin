#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Adriano Monteiro Marques
#
# Authors: Amit Pal <amix.pal@gmail.com>
#          Piotrek Wasilewski <wasilewski.piotrek@gmail.com>
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

from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    in_search = models.BooleanField(default=True,
        help_text=_('Show my profile in search results'))
    is_public = models.BooleanField(default=True,
        help_text=_('Let others to see my public profile'))
    timezone = models.CharField(max_length=30, null=False, blank=False,
                                help_text=_("Select the local timezone"))
    skype = models.CharField(max_length=20, blank=True)
    irc = models.CharField(max_length=20, blank=True)
    website = models.CharField(max_length=30, blank=True)
    private_key = models.CharField(max_length=500, blank=True)
    
    def __unicode__(self):
        return 'Profile for user %s' % self.user.username
    
    @permalink
    def get_absolute_url(self):
        return ('user_profile_public', [str(self.user.username)])

    @property
    def full_name(self):
        f_name, l_name = self.user.first_name, self.user.last_name
        if f_name and l_name:
            return '%s %s' % (f_name, l_name)
        return f_name or l_name or self.user.username
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
post_save.connect(create_user_profile, sender=User)

class UserActivationCode(models.Model):
    user = models.OneToOneField(User)
    code = models.CharField(max_length=30)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "Activation code %s for user %s" % \
                (self.code, self.user.username)

    @permalink                
    def get_absolute_url(self):
        return ('user_activation', [str(self.code)])
    
    def is_active(self):
        expiration_date = self.date_created.replace(day=self.date_created.day+7)
        now = datetime.datetime.now()
        if now < expiration_date:
            return True
        return False
