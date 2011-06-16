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

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import *
from reportmeta.models import ReportMeta, ReportMetaEventType
from reportmeta.forms import ReportMetaForm, ReportMetaNewForm
from networks.models import Host, Network
from events.models import Event, EventType

@login_required
def reports(request):
    """Displays reports starting page"""
    host_content_type = ContentType.objects.get_for_model(Host)
    net_content_type = ContentType.objects.get_for_model(Network)
    context = {
        'host_reports': ReportMeta.objects.filter(object_type=host_content_type),
        'net_reports': ReportMeta.objects.filter(object_type=net_content_type)
    }
    return direct_to_template(request, 'reportmeta/reports.html', extra_context=context)

@login_required
def reportmeta_detail(request, object_id):
    queryset = ReportMeta.objects.all()
    return object_detail(request, queryset, object_id)

@login_required
def reportmeta_list(request, object_type):
    """Displays list of reports"""
    if object_type == 'host':
        model = Host
    else:
        model = Network
    content_type = ContentType.objects.get_for_model(model)
    queryset = ReportMeta.objects.filter(object_type=content_type.pk)
    context = {
        'object_type': object_type
    }
    return object_list(request, queryset, extra_context=context)

@login_required
def reportmeta_new_from_object(request, object_type, object_id):
    """Displays new report form"""
    
    if not request.user.has_perm('reportmeta.add_reportmeta'):
        return direct_to_template(request, "no_permissions.html")
    
    if request.method == 'POST':
        form = ReportMetaForm(request.POST)
        if form.is_valid():
            reportmeta = form.save()
            return redirect_to(request, url=reportmeta.get_absolute_url())
    
    if object_type == 'host':
        model = Host
    else:
        model = Network
    content_type = ContentType.objects.get_for_model(model)
    object_name = model.objects.get(pk=object_id).name
    
    initial = {
        'object_type': content_type.pk,
        'object_id': object_id
    }
    form = ReportMetaForm(initial=initial)
    
    context = {
        'form': form,
        'object_name': object_name,
        'object_type_name': object_type,
    }
    return direct_to_template(request, 'reportmeta/reportmeta_form.html', extra_context=context)

@login_required
def reportmeta_new(request, object_type):
    
    if not request.user.has_perm('reportmeta.add_reportmeta'):
        return direct_to_template(request, "no_permissions.html")
    
    if request.method == 'POST':
        form = ReportMetaForm(request.POST)
        if form.is_valid():
            reportmeta = form.save()
            return redirect_to(request, url=reportmeta.get_absolute_url(), permanent=False)
        
    if object_type == 'host':
        model = Host
    else:
        model = Network
    content_type = ContentType.objects.get_for_model(model)
    
    objects_list = model.objects.all() 
    
    
    initial = {
        'object_type': content_type.pk,
        'user': request.user.pk
    }
    form = ReportMetaNewForm(initial=initial)
    
    context = {
        'form': form,
        'objects_list': objects_list,
        'object_type_name': object_type,
    }
    
    return direct_to_template(request, 'reportmeta/reportmeta_form.html', extra_context=context)

@login_required
def reportmeta_update(request, object_id):
    
    if not request.user.has_perm('reportmeta.change_reportmeta'):
        return direct_to_template(request, "no_permissions.html")
    
    if request.method == 'POST':
        report_meta = ReportMeta.objects.get(pk=object_id)
        form = ReportMetaForm(request.POST, instance=report_meta)
        if form.is_valid():
            form.save()
            types_updated = request.POST.getlist('event_types')
            
            relations = ReportMetaEventType.objects.filter(report_meta=report_meta).select_related()
            for rel in relations:
                if rel.event_type.pk not in types_updated:
                    rel.delete()
            
            # create all newly selected relations
            for pk in types_updated:
                try:
                    rel = ReportMetaEventType.objects.get(report_meta=report_meta, event_type__pk=pk)
                except ReportMetaEventType.DoesNotExist:
                    event_type = EventType.objects.get(pk=pk)
                    rel = ReportMetaEventType(report_meta=report_meta, event_type=event_type)
                    rel.save()
                    
            return redirect_to(request,
                        reverse('reportmeta_update', args=[object_id]), permanent=False)
    
    context = {
        'event_types': EventType.objects.all()
    }
    return update_object(request, form_class=ReportMetaForm, object_id=object_id,
                         extra_context=context, template_name="reportmeta/reportmeta_update.html")

def reportmeta_delete(request, object_id):
    
    if not request.user.has_perm('reportmeta.detele_reportmeta'):
        return direct_to_template(request, "no_permissions.html")
    
    return delete_object(request, object_id=object_id,
                         model=ReportMeta,
                         post_delete_redirect=reverse('reportmeta_list', args=['network']))
    
def reportmeta_get_report(request, object_id):
    from geraldo.generators import PDFGenerator
    report = ReportMeta.objects.get(pk=object_id, user=request.user).report
    response = HttpResponse(mimetype='application/pdf')
    report.generate_by(PDFGenerator, filename=response)
    return response