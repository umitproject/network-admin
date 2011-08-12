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

from netadmin.plugins.core import load_plugins

def actions_list(active=False):
    """Returns list of actions as tuples: (action_name, callback)
    """
    plugins = load_plugins(active)
    actions = []
    for plugin in plugins:
        actions.extend(plugin.actions())
    return actions

def run_action(action_name, arg, pass_result=False):
    """
    Runs all callbacks for specified action. If pass_result is True then
    every callback gets as an argument the result of a previous callback.
    Otherwise all callbacks gets the same argument which is arg.
    
    Function returns result of the last callback (by default: None).
    """
    actions = actions_list(active=True)
    result = arg
    first_callback = True
    for name, callback in actions:
        if name == action_name:
            if pass_result:
                result = callback(result)
            else:
                result = callback(arg)
            first_callback = False
    return result
