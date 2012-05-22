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

from django import forms
from datetime import datetime
import pytz
from pytz import timezone
import pdb

from models import Host, Network


class HostCreateForm(forms.ModelForm):
    timezone2 = forms.ChoiceField(choices=[(x, x) for x in pytz.common_timezones], label=("TimeZone"))
    def save(self, commit=True):
        host1 = super(HostCreateForm, self).save(commit=False)
        host1.timezone=self.cleaned_data["timezone2"]
        host1.save()
        return host1
        
    class Meta:
        model = Host
        widgets = {
            'user': forms.HiddenInput(),
            'timezone': forms.HiddenInput()
        }
    
        
class HostUpdateForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ('name', 'description')
        
class NetworkCreateForm(forms.ModelForm):
    class Meta:
        model = Network
        widgets = {
            'user': forms.HiddenInput()
        }
        
class NetworkUpdateForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = ('name', 'description')
