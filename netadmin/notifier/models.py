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
DAYS_OF_WEEK = (
    _EVERY,
    (0, _("Monday")),
    (1, _("Tuesday")),
    (2, _("Wednesday")),
    (3, _("Thursday")),
    (4, _("Friday")),
    (5, _("Saturday")),
    (6, _("Sunday"))
)

    
class NotifierContainer(models.Model):
    """
    Base class for all types of containers used to plan
    sending the notification.
    """
    user = models.ForeignKey(User)
    
    def message(self):
        return _("No message specified")
    
    def attachment(self):
        return None
    
    class Meta:
        abstract = True
        
class NotifierQueueItem(NotifierContainer):
    """
    Simple container supposed to work as a FIFO queue.
    """
    timestamp = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return "Item added to queue at %s" % str(self.timestamp)
    
    class Meta:
        abstract = True
            
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
    minute = models.SmallIntegerField(choices=MINUTE_CHOICES, default=0)
    hour = models.SmallIntegerField(choices=HOUR_CHOICES, default=0)
    day_of_month = models.SmallIntegerField(choices=DAY_CHOICES, default=-1)
    day_of_week = models.SmallIntegerField(choices=DAYS_OF_WEEK, default=-1)
    
    def __unicode__(self):
        return "Job scheduled for day %i, hour %i, minute %i" % \
            (self.day_of_month, self.hour, self.minute)
            
    def set_daily(self, minute, hour):
        self.day_of_month = self.day_of_week = -1
        self.minute = minute
        self.hour = hour
        
    def set_weekly(self, minute, hour, day_of_week):
        self.day_of_month = -1
        self.minute = minute
        self.hour = hour
        self.day_of_week = day_of_week
        
    def set_monthly(self, minute, hour, day_of_month):
        self.day_of_week = -1
        self.minute = minute
        self.hour = hour
        self.day_of_month = day_of_month
        
    def set(self, minute, hour, day_of_month=None, day_of_week=None):
        if day_of_month:
            self.set_monthly(minute, hour, day_of_month)
        elif day_of_week:
            self.set_weekly(minute, hour, day_of_week)
        else:
            self.set_daily(minute, hour)
            
    class Meta:
        abstract = True
