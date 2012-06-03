#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Amit Pal <amix.pal@gmail.com>
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
from django.forms.models import modelformset_factory
from django.forms.widgets import RadioSelect, Select
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext as _

from models import EventType, Event, EventTypeCategory, EventComment


YEARS_RANGE = range(2000, datetime.datetime.now().year + 1)
_years_widget = SelectDateWidget(years=YEARS_RANGE)

class EventSearchSimpleForm(forms.Form):
    message = forms.CharField(max_length=150, label=_("Search for message"),
                              required=False)

class EventSearchForm(EventSearchSimpleForm):
    event_type = forms.ChoiceField()
    date_after = forms.DateField(label=_("After"), required=False, 
                                 widget=_years_widget)
    date_before = forms.DateField(label=_("Before"), required=False,
                                  widget=_years_widget)
    
    def __init__(self, user, *args, **kwargs):
        super(EventSearchForm, self).__init__(*args, **kwargs)
        # filter event types by user access
        event_types = EventType.objects.filter(user=user)
        choices = [('0', 'any')] + [(et.pk, et.name) for et in event_types]
        self.fields['event_type'] = forms.ChoiceField(choices=choices,
                                                      label=_("Type"))

class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ('name', 'alert_level', 'notify')
        widgets = {
            'name': forms.HiddenInput()
        }

EventTypeFormset = modelformset_factory(EventType, form=EventTypeForm, extra=0)

class EventCategoryForm(forms.ModelForm):
    class Meta:
        model = EventTypeCategory
        fields = ('name', 'slug', 'user')
        widgets = {
            'user': forms.HiddenInput()
        }

EventCategoryFormset = modelformset_factory(EventTypeCategory,
                                            form=EventCategoryForm, extra=0)

class EventCheckForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('checked', )

class EventCommentForm(forms.ModelForm):
    class Meta:
        model = EventComment
        fields = ('comment', 'user', 'event')
        widgets = {
            'user': forms.HiddenInput()
            }
EventCommentFormset = modelformset_factory(EventComment,
                                            form = EventCommentForm)
