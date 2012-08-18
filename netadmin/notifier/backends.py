#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Adriano Monteiro Marques
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

import itertools

from django.core.mail.message import EmailMultiAlternatives
from django.utils.translation import ugettext as _
try:
	from Skype4Py import Skype
except ImportError:
	Skype = None

import sys
try:
    from django.conf.settings import NOTIFICATION_BACKEND_EMAIL_FROM
except ImportError:
    NOTIFICATION_BACKEND_EMAIL_FROM = 'noreply@localhost'


class UnknownEMailAddress(Exception):
    pass


class BaseBackend(object):
    """Base class of notifications backend
    """
    __identifier__ = 'base'

    def send(self, queryset):
        """
        Iterates over the notifications queryset and sends every notification
        """
        pass


class EMailBackend(BaseBackend):
    __identifier__ = 'e-mail'

    subject = _("Notifications from the Network Administrator")
    text_separator = '\n\n'
    html_separator = '<br /><hr /><br />'
    
    def __init__(self, from_address=NOTIFICATION_BACKEND_EMAIL_FROM):
        self.from_address = from_address

    def to_text(self, notification):
        underline = '=' * len(notification.title)
        return '%s\n%s\n%s' % \
               (notification.title, underline, notification.content)

    def to_html(self, notification):
        return '<h2>%s</h2><p>%s</p>' % \
               (notification.title, notification.content)

    def send(self, queryset):
        try:
            queryset = queryset.order_by('user_id')
        except AttributeError:
            notification = queryset

            text_msg = self.to_text(notification)
            html_msg = self.to_html(notification)
            to_address = notification.user.email
            email = EmailMultiAlternatives(self.subject, text_msg,
                                           self.from_address, [to_address])
            email.attach_alternative(html_msg, "text/html")
            email.send()
            
            return email

        emails = []
        for key, group in itertools.groupby(queryset.order_by('user_id'),
                                            lambda notif: notif.user.email):
            if not key:
                raise UnknownEMailAddress()

            html_messages, text_messages = [], []
            for notification in group:
                html_messages.append(self.to_html(notification))
                text_messages.append(self.to_text(notification))
            text_message = self.text_separator.join(text_messages)
            html_message = self.html_separator.join(html_messages)

            to_address = key

            email = EmailMultiAlternatives(self.subject, text_message,
                                           self.from_address, [to_address])
            email.attach_alternative(html_message, "text/html")
            emails.append(email)

        for email in emails:
            email.send()

        return emails

class SkypeBackend(BaseBackend):
	__identifier__ = 'skype'
	
	Title = "Notifications from the Network Administrator"
	
	def to_text(slef, notification):
		underline = '=' * len(notification.title)
		return '%s\n%s\n%s' % \
				(notification.title, underline, notification.content)
		
	def send(self, queryset):
		try:
			queryset = queryset.order_by('user_id')
		except AttributeError:
			notification = queryset
        
		test_message = self.to_text(notification)
		test_user = slef.to_user(notification.user.skype)
		client = Skype(Transport='x11')
		client.Attach()
		client.SendMessage(test_user,test_message)
		return test_user
