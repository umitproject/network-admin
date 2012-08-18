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

from django.utils.translation import ugettext as _
from netadmin.shortcuts import get_hosts, get_commands
from netadmin.plugins import Plugin, Widget
from netadmin.networks.models import HostCommand

class CommandExecWidget(Widget):
    name = _("command execution")
    description = _("Execute the commands on remote hosts")
    template_name = "command_exec.html"
    username = []
		
    def get_title(self, widget):
		title = self.get_option('latest_events_widget_title', widget)
		return title
    
    def options(self, widget):
        return {
            'number_of_commands': {
                'label': _("Number of command to show"),
                'choices': [(i, i) for i in xrange(1, 16)],
                'default': 5
            }
        }
        
	def context(self, widget):
		command_obj = get_commands(user=self.user)
		limit = self.get_option('number_of_commands', widget)
		return {
			'command_obj': command_obj[:limit]
		}
		
class CommandExec(Plugin):
    name = _("commands execution")
    description = _("Execute the commands on remote host")
    author = "Amit Pal"
    
    def widgets(self):
        return [CommandExecWidget]
    
__plugins__ = [CommandExec]
