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

from django import template

from netadmin.events.models import Alert, ALERT_LEVELS


register = template.Library()


@register.inclusion_tag('events/alerts_counter.html')
def alerts_counter(user_id):
    user_alerts = Alert.objects.filter(user__pk=user_id)
    alert_levels = []
    for id, name in ALERT_LEVELS:
        alerts = user_alerts.filter(level=id)
        count = 0
        for alert in alerts:
            count += alert.event_type.events.count()
        alert_levels.append((id, name, count))
    return {'alert_levels': alert_levels}
