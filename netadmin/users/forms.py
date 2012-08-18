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
from django.forms.models import modelformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from datetime import datetime
try:
	import pytz
except ImportError:
	pytz = None

from models import UserProfile
from netadmin.notifier.models import Notifier


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('is_public', 'in_search','website','skype','irc','private_key')
        
class UserRegistrationForm(UserCreationForm):
    email2 = forms.EmailField(label=_("E-mail"))
    timezone2 = forms.ChoiceField(choices=[(x, x) for x in pytz.common_timezones], 
                                 label = _("TimeZone"))
    
    def clean_email2(self):
        email2 = self.cleaned_data['email2']
        try:
            user = User.objects.get(email=email2)
        except User.DoesNotExist:
            return email2
        raise forms.ValidationError(_("Account with this e-mail address already exists."))
    
    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email2"]
        user.is_active = False
        if commit:
            user.save()
            user_profile = user.get_profile()
            user_profile.timezone = self.cleaned_data["timezone2"]
            user_profile.save()
        return user

                                            
class EventNotifierForm(forms.ModelForm):
	class Meta:
		model = Notifier
		fields = ('high', 'medium', 'low', 
				  'user')
		widgets = {
			'user': forms.HiddenInput()
		}
		
NotifierFormset = modelformset_factory(Notifier, form=EventNotifierForm)						               
