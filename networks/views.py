from django.views.generic.list_detail import object_detail
from events.models import Event
from networks.models import Host, Network, NetworkHost

def host_detail(request, object_id):
    queryset = Host.objects.all()
    host = Host.objects.get(pk=object_id)
    extra_context = {
        'events': Event.objects.filter(source_host=host)
    }
    return object_detail(request, queryset, object_id, extra_context=extra_context)

def network_detail(request, object_id):
    queryset = Network.objects.all()
    network = Network.objects.get(pk=object_id)
    related_hosts = [nh.host.pk for nh in NetworkHost.objects.filter(network=network)]
    hosts = Host.objects.filter(pk__in=related_hosts)
    extra_context = {
        'hosts': hosts
    }
    return object_detail(request, queryset, object_id, extra_context=extra_context)