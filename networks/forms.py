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
from networks.models import Host, Network

class HostCreateForm(forms.ModelForm):
    class Meta:
        model = Host
        widgets = {
            'user': forms.HiddenInput()
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