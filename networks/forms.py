from django import forms
from networks.models import Host

class HostCreateForm(forms.ModelForm):
    class Meta:
        model = Host
        
class HostUpdateForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ('name', 'description')