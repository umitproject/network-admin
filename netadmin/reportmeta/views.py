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

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import *

from netadmin.reportmeta.models import ReportMeta, ReportMetaEventType, \
    ReportNotification
from netadmin.reportmeta.forms import ReportMetaForm, ReportMetaNewForm
from netadmin.networks.models import Host, Network
from netadmin.notifier.utils import NotifierSchedule
from netadmin.events.models import Event, EventType


@login_required
def reports(request):
    """Displays reports starting page"""
    host_content_type = ContentType.objects.get_for_model(Host)
    net_content_type = ContentType.objects.get_for_model(Network)
    context = {
        'host_reports': ReportMeta.objects.filter(object_type=host_content_type,
                                                  user=request.user),
        'net_reports': ReportMeta.objects.filter(object_type=net_content_type,
                                                 user=request.user)
    }
    return direct_to_template(request, 'reportmeta/reports.html',
                              extra_context=context)

@login_required
def reportmeta_detail(request, object_id):
    queryset = ReportMeta.objects.filter(user=request.user)
    return object_detail(request, queryset, object_id)

@login_required
def reportmeta_list(request, object_type):
    """Displays list of reports"""
    if object_type == 'host':
        model = Host
    else:
        model = Network
    content_type = ContentType.objects.get_for_model(model)
    queryset = ReportMeta.objects.filter(object_type=content_type.pk,
                                         user=request.user)
    context = {
        'object_type': object_type
    }
    return object_list(request, queryset, extra_context=context)

@login_required
def reportmeta_new_from_object(request, object_type, object_id):
    """Displays new report form"""
    form = None
    if request.method == 'POST':
        form = ReportMetaForm(request.POST)
        if form.is_valid():
            reportmeta = form.save()
            notif = ReportNotification(report_meta=reportmeta,
                                       user=reportmeta.user)
            notif.save()
            return redirect_to(request, url=reportmeta.get_absolute_url())
    
    if object_type == 'host':
        model = Host
    else:
        model = Network
    content_type = ContentType.objects.get_for_model(model)
    object_name = model.objects.get(pk=object_id).name
    
    initial = {
        'object_type': content_type.pk,
        'object_id': object_id,
        'user': request.user.pk
    }
    if not form:
        form = ReportMetaForm(initial=initial)
    
    context = {
        'form': form,
        'object_name': object_name,
        'object_type_name': object_type,
    }
    
    return direct_to_template(request, 'reportmeta/reportmeta_form.html',
                              extra_context=context)

@login_required
def reportmeta_new(request, object_type):
    if request.method == 'POST':
        form = ReportMetaForm(request.POST)
        if form.is_valid():
            reportmeta = form.save()
            notif = ReportNotification(report_meta=reportmeta,
                                       user=reportmeta.user)
            notif.save()
            url = reportmeta.get_absolute_url()
            return redirect_to(request, url=url, permanent=False)
        
    if object_type == 'host':
        model = Host
    else:
        model = Network
    content_type = ContentType.objects.get_for_model(model)
    objects_list = model.objects.filter(user=request.user) 
    
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
    
    return direct_to_template(request, 'reportmeta/reportmeta_form.html',
                              extra_context=context)

@login_required
def reportmeta_update(request, object_id):
    report_meta = ReportMeta.objects.get(pk=object_id)
    
    notif, cr = ReportNotification.objects.get_or_create(report_meta=report_meta,
                                                         user=report_meta.user)
    schedule_form_class = report_meta.get_notification_form_class()
    
    if request.method == 'POST':
        report_form = ReportMetaForm(request.POST, instance=report_meta)
        schedule_form = schedule_form_class(request.POST)
        if report_form.is_valid():
            report_form.save()
            types_updated = request.POST.getlist('event_types')
            
            # delete deselected relations
            relations = ReportMetaEventType.objects.filter(report_meta=report_meta)
            for rel in relations:
                if rel.event_type.pk not in types_updated:
                    rel.delete()
            
            # create all newly selected relations
            for pk in types_updated:
                try:
                    rel = ReportMetaEventType.objects.get(report_meta=report_meta,
                                                          event_type__pk=pk)
                except ReportMetaEventType.DoesNotExist:
                    event_type = EventType.objects.get(pk=pk)
                    rel = ReportMetaEventType(report_meta=report_meta,
                                              event_type=event_type)
                    rel.save()
                    
            # update report notification
            if schedule_form.is_valid():
                notif.set(**schedule_form.cleaned_data)
                notif.save()
                    
            redirect_url = reverse('reportmeta_update', args=[object_id])
            return redirect_to(request, redirect_url, permanent=False)
    else:
        initial = {
            'hour': notif.hour,
            'minute': notif.minute,
            'day_of_week': notif.day_of_week if notif.day_of_week > 0 else 1,
            'day_of_month': notif.day_of_month if notif.day_of_month > 0 else 1
        }
        schedule_form = schedule_form_class(initial)
    
    context = {
        'event_types': EventType.objects.all(),
        'schedule_form': schedule_form
    }
    return update_object(request, form_class=ReportMetaForm,
                         object_id=object_id, extra_context=context,
                         template_name="reportmeta/reportmeta_update.html")

@login_required
def reportmeta_delete(request, object_id):
    report_meta = ReportMeta.object.get(pk=object_id)
    
    redirect_url = reverse('reports')
    
    if report_meta.user != request.user:
        return redirect_to(request, redirect_url, permanent=False)
    
    return delete_object(request, ReportMeta, redirect_url, object_id)

@login_required    
def reportmeta_get_report(request, object_id):
    from geraldo.generators import PDFGenerator
    report = ReportMeta.objects.get(pk=object_id, user=request.user).report
    response = HttpResponse(mimetype='application/pdf')
    report.generate_by(PDFGenerator, filename=response)
    return response

def reportmeta_send_emails(request):
    notifier = NotifierSchedule(ReportNotification)
    response = '<p><strong>%s</strong></p>' % datetime.datetime.now()
    log = notifier.send_emails(_("New report from in Network Administrator"))
    if log:
        response += "<p>Emails sent:</p>%s" % '<br />'.join(log)
    else:
        response += "<p>No emails to send</p>"
    return HttpResponse(response)