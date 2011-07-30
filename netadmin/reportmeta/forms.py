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

from django import forms
from django.utils.translation import ugettext as _

from netadmin.reportmeta.models import ReportMeta


DAYS_OF_WEEK = (
    (1, _("Monday")),
    (2, _("Tuesday")),
    (3, _("Wednesday")),
    (4, _("Thursday")),
    (5, _("Friday")),
    (6, _("Saturday")),
    (7, _("Sunday"))
)

DAYS_OF_MONTH = [(day, day) for day in xrange(1, 32)]

MINUTES = [(minute, minute) for minute in xrange(0, 60)]

HOURS = [(hour, hour) for hour in xrange(0, 24)]


class ReportMetaForm(forms.ModelForm):
    class Meta:
        model = ReportMeta
        widgets = {
            'object_id': forms.HiddenInput(),
            'object_type': forms.HiddenInput(),
            'user': forms.HiddenInput()
        }
        
class ReportMetaNewForm(forms.ModelForm):
    class Meta:
        model = ReportMeta
        fields = ('name', 'description', 'object_type', 'user',
                  'report_period')
        widgets = {
            'object_type': forms.HiddenInput(),
            'user': forms.HiddenInput()
        }
        
class ReportDailyForm(forms.Form):
    hour = forms.ChoiceField(choices=HOURS, initial=0)
    minute = forms.ChoiceField(choices=MINUTES, initial=0)
    
class ReportWeeklyForm(ReportDailyForm):
    day_of_week = forms.ChoiceField(choices=DAYS_OF_WEEK, initial=1)

class ReportMonthlyForm(ReportDailyForm):
    day_of_month = forms.ChoiceField(choices=DAYS_OF_MONTH, initial=1)
