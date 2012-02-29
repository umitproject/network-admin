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
import StringIO

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from geraldo.generators import PDFGenerator

from netadmin.networks.reports import HostReport, NetworkReport
from netadmin.events.models import EventType


DAILY = 0
WEEKLY = 1
MONTHLY = 2

REPORT_PERIOD = (
    (DAILY, _("Daily")),
    (WEEKLY, _("Weekly")),
    (MONTHLY, _("Monthly"))
)

SEND_HOURS = tuple((hour, hour) for hour in xrange(24))
SEND_DAYS = tuple((day, day) for day in xrange(1, 32))


class ReportMeta(models.Model):
    """
    Report Meta class contains all report metadata like its name,
    description, time period and reported object. 
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    period = models.IntegerField(choices=REPORT_PERIOD, default=0)
    send_hour = models.SmallIntegerField(choices=SEND_HOURS, default=12)
    send_day = models.SmallIntegerField(choices=SEND_DAYS, default=1)
    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    user = models.ForeignKey(User)

    reported_object = generic.GenericForeignKey('object_type', 'object_id')
    
    def __unicode__(self):
        return "Report for %s" % self.reported_object.name

    def save(self, *args, **kwargs):
        if self.period == WEEKLY and self.send_day > 7:
            raise Exception("Cannot set send_day > 7 for a weekly report")
        super(ReportMeta, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('reportmeta_detail', args=[self.pk])
    
    def delete(self, *args, **kwargs):
        related = ReportMetaEventType.objects.filter(report_meta=self)
        related.delete()
        super(ReportMeta, self).delete(*args, **kwargs)
        
    def get_object_model(self):
        return self.object_type.model_class()
    model = property(get_object_model)
    
    def get_event_types(self):
        """Returns event types related to the report"""
        related = ReportMetaEventType.objects.filter(report_meta=self)
        pks = [e.event_type.pk for e in related]
        event_types = EventType.objects.filter(pk__in=pks)
        return event_types
    event_types = property(get_event_types)
    
    def get_events(self):
        """Returns events from host/network included in the report"""
        events = self.reported_object.events()
        pks = [et.pk for et in self.event_types]
        events = events.filter(event_type__pk__in=pks)
        
        now = datetime.datetime.now()
        date_from = None
        if self.period == 0:
            date_from = now.replace(day=now.day-1)
        elif self.period == 1:
            date_from = now.replace(day=now.day-7)
        elif self.period == 2:
            date_from = now.replace(month=now.month-1)
        if date_from:
            events = events.filter(timestamp__gte=date_from)
        
        return events
    
    def get_period_name(self):
        for number, name in REPORT_PERIOD:
            if number == self.period:
                return name
    
    def get_report(self):
        if self.model.__name__ == 'Host':
            return HostReport(self.name, queryset=self.get_events())
        elif self.model.__name__ == 'Network':
            return NetworkReport(self.name, queryset=self.get_events())
        else:
            return None

    def ready_to_send(self, date=None):
        if not date:
            date = datetime.datetime.now()

        if self.period == DAILY:
            if date.hour == self.send_hour:
                return True
        elif self.period == WEEKLY:
            weekday = date.weekday() + 1
            if weekday == self.send_day and date.hour == self.send_hour:
                return True
        else:
            if date.day == self.send_day and date.hour == self.send_hour:
                return True
            
        return False
        
class ReportMetaEventType(models.Model):
    """
    Many-to-many relationship between report meta objects
    and event types included in the reports
    """
    report_meta = models.ForeignKey(ReportMeta)
    event_type = models.ForeignKey(EventType)

