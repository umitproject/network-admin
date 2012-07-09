#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Adriano Monteiro Marques
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
from django.db import models
from django.utils.translation import ugettext as _


class Message(models.Model):
    """System-generated message addressed to a user
    """
    user = models.ForeignKey(User, verbose_name=_("User"))
    content = models.CharField(_("Content"), max_length=255)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)

    def __unicode__(self):
        return "for %s at %s" % (self.user.username, self.timestamp)
