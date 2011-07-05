import datetime

from django import forms
from django.forms.widgets import RadioSelect, Select
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext as _

from events.models import EventType 


EVENT_TYPES = [(et.pk, et.name) for et in EventType.objects.all()]
EVENT_TYPE_CHOICES = [('0', 'any')] + EVENT_TYPES

YEARS_RANGE = range(2000, datetime.datetime.now().year + 1)

class EventSearchSimpleForm(forms.Form):
    message = forms.CharField(max_length=150, label=_("Search for message"),
                              required=False)

class EventSearchForm(EventSearchSimpleForm):
    event_type = forms.ChoiceField(choices=EVENT_TYPE_CHOICES, initial=0,
                                   widget=RadioSelect, label=_("Type"))
    date_after = forms.DateField(label=_("After"), required=False, 
                                 widget=SelectDateWidget(years=YEARS_RANGE))
    date_before = forms.DateField(label=_("Before"), required=False,
                                  widget=SelectDateWidget(years=YEARS_RANGE))