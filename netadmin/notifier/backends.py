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
    
    def __init__(self, from_address=NOTIFICATION_BACKEND_EMAIL_FROM):
        self.from_address = from_address

    def send(self, queryset):
        emails = []
        for key, group in itertools.groupby(queryset.order_by('user_id'),
                                            lambda notif: notif.user.email):
            if not key:
                raise UnknownEMailAddress()
            html_messages = []
            text_messages = []
            for notif in group:
                html_messages.append('<h2>%s</h2><p>%s</p>' % \
                                     (notif.title, notif.content))
                text_messages.append('%s\n=====\n%s' % \
                                     (notif.title, notif.content))
            text_message = '\n'.join(text_messages)
            html_message = '<br /><hr /><br />'.join(html_messages)
            subject = _("Notifications from the Network Administrator")
            to_address = key
            email = EmailMultiAlternatives(subject, text_message,
                                           self.from_address, [to_address])
            email.attach_alternative(html_message, "text/html")
            emails.append(email)

        for email in emails:
            email.send()

        return emails
