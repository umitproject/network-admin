from django import forms
from networks.models import Host, Network

class HostCreateForm(forms.ModelForm):
    class Meta:
        model = Host
        
class HostUpdateForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ('name', 'description')
        
class NetworkCreateForm(forms.ModelForm):
    class Meta:
        model = Network
        
class NetworkUpdateForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = ('name', 'description')