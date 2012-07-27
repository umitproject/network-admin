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

import inspect

from netadmin.notifier.backends import BaseBackend
from netadmin.notifier.models import Notification


class BackendError(Exception):
    pass

class NoBackendsAvailable(BackendError):
    pass

class UnknownBackend(BackendError):
    pass

class NotificationBufferEmpty(Exception):
    pass


class Dispatcher(object):
    _backends = []

    def __init__(self, manager):
        self.manager = manager

    def _get_backends(self):
        from netadmin.notifier import backends
        backends_list = []
        for obj_name, obj in inspect.getmembers(backends):
            if hasattr(obj, '__bases__') and BaseBackend in obj.__bases__:
                backends_list.append(obj)
        return backends_list

    def _refresh_backends(self):
        self._backends = self._get_backends()

    def get_backend(self, identifier):
        self._refresh_backends()
        for backend in self._backends:
            if backend.__identifier__ == identifier:
                return backend()
        raise UnknownBackend("Unknown backend: %s" % identifier)

    def iter_backends(self):
        """Iterates over all available notification back-ends
        """
        self._refresh_backends()

        if not self._backends:
            raise NoBackendsAvailable()

        for backend in self._backends:
            yield backend()

    def dispatch(self, notification_type, using_backends=None, clear=True):
        """Sends all notifications using available back-ends
        """
        notifications = self.manager.get_all()
        
        if using_backends:
            backends = [self.get_backend(id) for id in using_backends]
        else:
            backends = self.iter_backends()

        for backend in backends:
            backend.send(notifications)

        if clear:
            self.manager.clear()


class NotificationsManager(object):
    _buffer = []

    def get_all(self):
        """Returns all notifications
        """
        self._buffer = Notification.objects.all()
        return self._buffer

    def create(self, title, content, user, related_object=None):
        """Creates a new notification but DO NOT SAVES that notification
        """
        return Notification(title=title, content=content, user=user,
                            related_object=related_object)

    def add(self, title, content, user, related_object=None):
        """Creates notification and saves it
        """
        notification = self.create(title, content, user, related_object)
        notification.save()
        return notification

    def clear(self):
        """Deletes all notifications that were fetched using get_all() method
        """
        if self._buffer:
            self._buffer.delete()
            self._buffer = []
        else:
            raise NotificationBufferEmpty()


manager = NotificationsManager()
dispatcher = Dispatcher(manager)

def get_notifier(notifier):
	if notifier == 0:
		return 'e-mail'
	elif notifier == 1:
		return 'skype'
	elif notifier == 2:
		return 'irc'
