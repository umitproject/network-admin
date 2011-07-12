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

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

from netadmin.networks.reports import HostReport, NetworkReport
from netadmin.events.models import EventType


PERIODS = (
    (1, _('Daily')),
    (7, _('Weekly')),
    (31, _('Monthly'))
)

class ReportMeta(models.Model):
    """
    Report Meta class contains all report metadata like its name,
    description, time period and reported object. 
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    period = models.IntegerField(choices=PERIODS)
    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    reported_object = generic.GenericForeignKey('object_type', 'object_id')
    user = models.ForeignKey(User)
    
    def __unicode__(self):
        return "Report for %s" % self.reported_object.name
    
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
        events = self.reported_object.events
        pks = [et.pk for et in self.event_types]
        return events.filter(event_type__pk__in=pks)
    events = property(get_events)
    
    def get_period(self):
        for period_number, period_name in PERIODS:
            if period_number == self.period:
                return period_name
    
    def get_report(self):
        if self.model.__name__ == 'Host':
            return HostReport(queryset=[self.reported_object])
        elif self.model.__name__ == 'Network':
            return NetworkReport(queryset=[self.reported_object])
        else:
            return None
    report = property(get_report)
    
admin.site.register(ReportMeta)
        
class ReportMetaEventType(models.Model):
    """
    Many-to-many relationship between report meta objects
    and event types included in the reports
    """
    report_meta = models.ForeignKey(ReportMeta)
    event_type = models.ForeignKey(EventType)
    
admin.site.register(ReportMetaEventType)
