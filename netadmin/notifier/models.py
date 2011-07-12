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
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _


_EVERY = (-1, _('Every'))
MINUTE_CHOICES = [_EVERY] + [(min, min) for min in xrange(0, 60)]
HOUR_CHOICES = [_EVERY] + [(hour, hour) for hour in xrange(0, 24)]
DAY_CHOICES = [_EVERY] + [(day, day) for day in xrange(1, 32)]


class Notification(models.Model):
    """
    Notification class represents object which has to be reported
    to the user. The medium is not important here: there should be
    separate code that will decide how to deliver the notification.
    """
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def __unicode__(self):
        return "Notification for %s owned by %s" % \
            (self.content_type.name, self.user.username)
    
class NotifierContainer(models.Model):
    """
    Base class for all types of containers used to plan
    sending the notification.
    """
    notification = models.ForeignKey(Notification)
    
    class Meta:
        abstract = True
        
class NotifierQueueItem(NotifierContainer):
    """
    Simple container supposed to work as a FIFO queue.
    """
    timestamp = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return "Item added to queue at %s" % str(self.timestamp)
            
class NotifierScheduleJob(NotifierContainer):
    """
    Cron-like scheduler limited to day-of-month, hour and minute.
    Table below shows examples of usage:
    
        minute    hour    day
        -1        -1      -1    every minute
        10        -1      -1    every 10th minute of every hour
        30        7       -1    everyday at 7:30
        40        15      27    every 27th day of month at 15:40
    """
    minute = models.SmallIntegerField(choices=MINUTE_CHOICES)
    hour = models.SmallIntegerField(choices=HOUR_CHOICES)
    day = models.SmallIntegerField(choices=DAY_CHOICES)
    
    def __unicode__(self):
        return "Job scheduled for day %i, hour %i, minute %i" % \
            (self.day, self.hour, self.minute)
