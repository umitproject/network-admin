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
from django.utils.translation import ugettext as _

from netadmin.utils.charts.chart_tools import CHART_TOOLS_PACKAGES, \
    InvalidChartsPackage


register = template.Library()


@register.inclusion_tag('charts/chart_tools/chart.html')
def chart(chart, width=None, height=None):
    if width:
        chart.width = width
    if height:
        chart.height = height
    return {'chart': chart}

@register.inclusion_tag('charts/chart_tools/annotatedtimeline.html')
def chart_annotatedtimeline(chart):
    return {'chart': chart}

@register.filter
def chart_hash(chart):
    return hash(chart)

@register.inclusion_tag('charts/chart_tools/init.html')
def init_charts(args):
    context = {
        'packages': args
    }
    return context

@register.tag('init_charts')
def init_charts(parser, token):
    args = token.contents.split()
    args = [arg.strip("'").encode('ascii') for arg in args[1:]]
    return InitChartNode(*args)

class InitChartNode(template.Node):
    def __init__(self, *args, **kwargs):
        for package in args:
            if package not in CHART_TOOLS_PACKAGES:
                raise InvalidChartsPackage(_("Unknown package '%s'") % package)
        self.packages = list(args)

    def render(self, context):
        return """
            <script type="text/javascript">
                google.load('visualization', '1', {'packages': %s });
                charts = []
            </script>
        """ % self.packages

@register.inclusion_tag('charts/chart_tools/show.html')
def show_charts():
    return