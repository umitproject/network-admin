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

import paramiko
from netadmin.shortcuts import get_host
from netadmin.users.models import UserProfile
from netadmin.networks.models import HostCommand, Host
from celery.schedules import crontab

def exec_command(user,command_obj):
	user_obj = UserProfile.objects.get(user=user)
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(get_host(command_obj.host).ipv4.encode('utf8'), 
				username=Host.objects.get(id=command_obj.host).name.unicode('utf8'), port=25, pkey=user_obj.private_key.encode('utf8'))
		stdin, stdout, stderr = ssh.exec_command(command_obj.command.encode('utf8'))
	return "<strong> Done! </strong>"

def exec_scheduler(user,command_obj):
	CELERYBEAT_SCHEDULE = {
		'execute the commands': {
			'task': 'netadmin.utils.command.exec_command',
			'schedule': crontab(hour=, minute=, day_of_week=),
			'args': (user,command_obj)
		},
	}
	return "<strong> Scheduler started </strong>"
	
	
	
	
