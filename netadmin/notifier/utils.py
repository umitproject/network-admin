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

from django.core.mail.message import EmailMessage
from django.utils.translation import ugettext as _
from settings import GAE_MAIL_ACCOUNT


class NotifierEmptyQueue(Exception):
    pass


class Notifier(object):
    
    _log_buffer = []
    
    def __init__(self, model):
        self.model = model
    
    def _log(self, message, timestamp=datetime.datetime.now()):
        str_message = '%s: %s' % (str(timestamp), message)
        self._log_buffer.append(str_message) 
        return str_message
    
    def _clear_log(self):
        self._log_buffer = []

class NotifierQueue(Notifier):
    """
    First-in first-out notifications queue. To reduce number of database
    queries, queue items are held in a buffer, which is updated after clearing
    the queue or when update is forced (e.g. in case of iteration).
    
    NOTE: The simplest and safest way of accessing the queue is to
    iterate through its items:
    
        >>> queue = NotifierQueue()
        >>> for item in queue:
        ...     print item.user, item.content_object
    """
    _buffer = []
    
    def __init__(self, model, buffer_size=10):
        self._buffer_size = buffer_size
        super(NotifierQueue, self).__init__(model)
        
    def __iter__(self):
        self._update_buffer(force_update=True)
        for item in self._buffer:
            yield item
        
    def _update_buffer(self, force_update=False):
        if len(self._buffer) < self._buffer_size or force_update:
            items = self.model.objects.all().order_by('timestamp')
            self._buffer = list(items[:self._buffer_size])
        
    def clear(self):
        """
        Gets all notifications from the buffer and removes them
        permanently from database.
        
        NOTE: This action cannot be undone so use this method very
        carefully (e.g. after sending notifications by email, when
        you're absolutely sure that you don't need them anymore)!
        """
        if self._buffer:
            while self._buffer:
                item = self._buffer.pop()
                item.delete()
        
    def push(self, *args, **kwargs):
        """Pushes item to the end of the queue and returns it
        """
        item = self.model(*args, **kwargs)
        item.save()
        self._update_buffer()
        return item
    
    def get(self):
        """Returns all items from the queue
        """
        self._update_buffer()
        return self._buffer
    items = property(get)
    
    def send_emails(self, subject, clear_queue=True):
        self._clear_log()
        notifications = self.items
        grouped_by_user = {}
        for notif in notifications:
            user = notif.user
            if user in grouped_by_user:
                grouped_by_user[user].append(notif)
            else:
                grouped_by_user[user] = [notif]
                
        for user in grouped_by_user:
            notifications = grouped_by_user[user]
            messages = []
            attachments = []
            for notif in notifications:
                messages.append(notif.message())
                
                att = notif.attachment()
                if att:
                    attachments.append(att)
            
            # separate messages with horizontal line
            html_message = '<br /><hr /><br />'.join(messages)
            email = EmailMessage(subject, html_message,
                                 GAE_MAIL_ACCOUNT, [user.email])
            for att in attachments:
                email.attach(att['name'], att['data'], att['mimetype'])   
            email.send()
            
            self._log(_("Message sent to: %s") % user.email)
        
        if clear_queue:
            self.clear()
        return self._log_buffer
        
class NotifierSchedule(Notifier):
    """
    Simplified cron-like job scheduler for sending notifications at
    specified time. For more information about scheduling, go to documentation
    of NotifierScheduleJob model class.
    
    NOTE: The best way of getting all scheduled jobs that should run
    at the moment is to use iterator, e.g.:
    
        >>> schedule = NotifierSchedule()
        >>> for notif in schedule:
        ...     print notif.user, notif.content_object
    """
    def __iter__(self):
        for job in self.current_jobs:
            yield job
        
    def get_jobs(self):
        """Returns all scheduled jobs
        """
        jobs = self.model.objects.all()
        return jobs.order_by('day_of_month', 'hour', 'minute')
    jobs = property(get_jobs)
    
    def jobs_for_timestamp(self, timestamp):
        """Returns jobs that should be run for specified timestamp
        """
        ts = timestamp
        minute, hour = ts.minute, ts.hour
        day_of_week, day_of_month = ts.weekday(), ts.day
        
        jobs = self.jobs
        jobs = jobs.filter(day_of_month__in=[-1, day_of_month])
        jobs = jobs.filter(day_of_week__in=[-1, day_of_week])
        jobs = jobs.filter(hour__in=[-1, hour])
        jobs = jobs.filter(minute__in=[-1, minute]) 
    
        return jobs
    
    def _current_jobs(self):
        """Returns jobs that should run at the moment
        """
        return self.jobs_for_timestamp(datetime.datetime.now())
    current_jobs = property(_current_jobs)
    
    def send_emails(self, subject):
        self._clear_log()
        for job in self.current_jobs:
            user, message, att = job.user, job.message(), job.attachment()
            email = EmailMessage(subject, message,
                                 GAE_MAIL_ACCOUNT, [user.email])
            if att:
                email.attach(att['name'], att['data'], att['mimetype'])   
            email.send()
            
            self._log(_("Message sent to: %s") % user.email)
        return self._log_buffer
