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

from django import forms
from django.forms.widgets import RadioSelect, Select
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext as _

from netadmin.events.models import EventType, Alert


EVENT_TYPES = [(et.pk, et.name) for et in EventType.objects.all()]
EVENT_TYPE_CHOICES = [('0', 'any')] + EVENT_TYPES

YEARS_RANGE = range(2000, datetime.datetime.now().year + 1)
_years_widget = SelectDateWidget(years=YEARS_RANGE)

class EventSearchSimpleForm(forms.Form):
    message = forms.CharField(max_length=150, label=_("Search for message"),
                              required=False)

class EventSearchForm(EventSearchSimpleForm):
    event_type = forms.ChoiceField(choices=EVENT_TYPE_CHOICES, initial=0,
                                   widget=RadioSelect, label=_("Type"))
    date_after = forms.DateField(label=_("After"), required=False, 
                                 widget=_years_widget)
    date_before = forms.DateField(label=_("Before"), required=False,
                                  widget=_years_widget)
    
class AlertForm(forms.ModelForm):
    
    def clean(self):
        # Since GAE doesn't support "unique" property, we have to
        # check it here if fields "user" and "event_type" are unique.
        cleaned_data = self.cleaned_data
        user = cleaned_data.get('user')
        event_type = cleaned_data.get('event_type')
        try:
            alert = Alert.objects.get(user=user, event_type=event_type)
        except Alert.DoesNotExist:
            return cleaned_data
        raise forms.ValidationError("Event type may be assigned to one "
                                    "level only.")
        
    class Meta:
        model = Alert
        widgets = {
            'user': forms.HiddenInput()
        }