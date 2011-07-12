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
from django.contrib.contenttypes.models import ContentType

from netadmin.notifier.models import NotifierQueueItem, NotifierScheduleJob, \
    Notification


class NotifierNoHTML(Exception):
    pass

class NotifierNoAttachment(Exception):
    pass

class NotifierEmptyQueue(Exception):
    pass

class NotifierValidationError(Exception):
    pass

class NotifierQueue(object):
    """
    First-in first-out notifications queue. To reduce number of database
    queries, queue items are held in a buffer, which is updated when clearing
    the queue or when update is forced (e.g. in case of iteration).
    
    NOTE: The simplest and safest way of accessing the queue is to
    iterate through its items:
    
        >>> queue = NotifierQueue()
        >>> for notif in queue:
        ...     print notif.user, notif.content_object
    """
    _buffer = []
    
    def __init__(self, buffer_size=10):
        self._buffer_size = buffer_size
        
    def __iter__(self):
        self._update_buffer(force_update=True)
        for item in self._buffer:
            yield item.notification
        
    def _update_buffer(self, force_update=False):
        if len(self._buffer) < self._buffer_size or force_update:
            items = NotifierQueueItem.objects.all().order_by('timestamp')
            self._buffer = [item for item in items]
        
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
        
    def push(self, obj, user):
        """Pushes item to the end of the queue and returns it
        """
        item = NotifierQueueItem(user=user, content_object=obj)
        item.save()
        self._update_buffer()
        return item
    
    def get(self):
        """Returns all items from the queue
        """
        self._update_buffer()
        return self._buffer
    items = property(get)
        
class NotifierSchedule(object):
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
            yield job.notification
        
    def get_jobs(self):
        """Returns all scheduled jobs
        """
        user_jobs = NotifierScheduleJob.objects.all()
        return user_jobs.order_by('day', 'hour', 'minute')
    jobs = property(get_jobs)
    
    def new_job(self, obj, user, minute=-1, hour=-1, day=-1):
        """Puts new job into schedule
        """
        job = NotifierScheduleJob(user=user, content_object=obj,
                                  minute=minute, hour=hour, day=day)
        job.save()
        return job
    
    def delete_job(self, obj, user):
        """Deletes user's scheduled job for specified object
        """
        jobs = self.jobs.filter(user=user)
        for job in jobs:
            if job.notification.content_object == obj:
                job.delete()
    
    def jobs_for_timestamp(self, timestamp):
        """Returns jobs that should be run for specified timestamp
        """
        ts = timestamp
        minute, hour, day = ts.minute, ts.hour, ts.day
        jobs = self.jobs
        
        # filter by day
        jobs = jobs.filter(day__in=[-1, day])
        # filter by hour
        jobs = jobs.filter(hour__in=[-1, hour])
        # filter by minute
        jobs = jobs.filter(minute__in=[-1, minute]) 
    
        return jobs
    
    def _current_jobs(self):
        """Returns jobs that should run at the moment
        """
        return self.jobs_for_timestamp(datetime.datetime.now())
    current_jobs = property(_current_jobs)

class Notifier(object):
    """
    Notifications manager designed for validating database consistency
    and sending notifications to users. It uses both queue and schedule. 
    """
    _log_buffer = []
    
    def __init__(self, queue_size=10):
        self.queue = NotifierQueue(buffer_size=queue_size)
        self.schedule = NotifierSchedule()
    
    def _log(self, timestamp, message):
        str_message = '%s: %s' % (str(timestamp), message)
        self._log_buffer.append(str_message) 
        return str_message
    
    def _clear_log(self):
        self._log_buffer = []
        
    def is_valid(self):
        """
        Returns true if every notification is linked to the queue only once
        or if it's linked only to schedule.
        
        IMPORTANT NOTE: Since this method runs quite heavy database queries,
        you should use it only when you have to be REALLY sure that database
        structure is consistent (e.g. when you start working with Notifier).
        """
        all_notifications = Notification.objects.all()
        for notif in all_notifications:
            queue_count = self.notifierqueueitem_set.all().count()
            schedule_count = self.notifierschedulejob_set.all().count()
            # if notification was put into queue more than once
            if queue_count > 1:
                return False
            # if notification is in both queue and schedule
            if queue_count and schedule_count:
                return False
        return True
    
    def validate(self):
        """
        Validates notifications using is_valid method. Check is_valid
        documentation for important notes!
        """
        # TODO
        # This method should also repair (or delete) invalid notifications
        if not self.is_valid():
            raise NotifierValidationError("Notifications are not valid. "
                                          "Please check database consistency")
        return True
        
    def notifications(self):
        """Returns all current notifications
        """
        return list(self.queue) + list(self.schedule)
        
    def _grouped_notifications(self):
        """
        Returns current notifications grouped by users, as a dictionary, where
        keys are users and values are lists of notifications.
        """
        notifications = self.notifications()
        
        grouped = {}
        for notif in notifications:
            user = notif.user
            if user in grouped:
                grouped[user].append(notif)
            else:
                grouped[user] = [notif]
                
        return grouped
    
    def send_emails(self, clear_queue=True, force_attachment=False):
        """Gets all current notifications and sends them to users 
        """
        grouped = self._grouped_notifications()
        
        self._clear_log()
        
        for user in grouped:
            notifications = grouped[user]
            messages = []
            attachments = []
            for notif in notifications:
                notif_obj = notif.content_object
                
                try:
                    messages.append(notif_obj.get_html())
                except AttributeError:
                    raise NotifierNoHTML("Can't get HTML message from "
                                         "the object")
                
                try:
                    attachments.append(notif_obj.get_attachment())
                except AttributeError:
                    if force_attachment:
                        raise NotifierNoAttachment("Can't get attachment "
                                                   "from the object")
            
            # separate messages with horizontal line
            html_message = '<br /><hr /><br />'.join(messages)
            title = "Your notifications from Network Administrator " \
                    "(do not reply to this message)"
            email = EmailMessage(title, html_message,
                                 'wasilewski.piotrek@gmail.com', [address])
            for att in attachments:
                email.attach(att['name'], att['file'], att['mimetype'])   
            email.send()
            
            self._log(datetime.datetime.now(), user.username)
            
            self.queue.clear()
        
        return self._log_buffer