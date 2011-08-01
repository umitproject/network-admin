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
from django.forms.models import modelformset_factory

from netadmin.plugins.core import load_plugins
from netadmin.plugins.models import PluginSettings


class PluginSettingsForm(forms.ModelForm):
    def get_meta(self):
        for plugin in load_plugins():
            meta = plugin().plugin_meta()
            if meta['name'] == self.instance.plugin_name:
                return meta
        return {}
    
    class Meta:
        model = PluginSettings
        
PluginSettingsFormset = modelformset_factory(PluginSettings,
                                             form=PluginSettingsForm)