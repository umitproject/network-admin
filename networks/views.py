from django.views.generic.list_detail import object_detail
from events.models import Event
from networks.models import Host, Network, NetworkHost

def host_detail(request, object_id):
    """Simple object detail page - additional view used to make code clearer"""
    queryset = Host.objects.all()
    host = Host.objects.get(pk=object_id)
    extra_context = {
        'events': Event.objects.filter(source_host=host)
    }
    return object_detail(request, queryset, object_id, extra_context=extra_context)

def network_detail(request, object_id):
    """
    Network detail page has the following features:
        * displaying basic network info (name, description, etc.)
        * listing hosts related to network
        * creating relations between network and host
        * removing relations between network and host(s)
    """
    
    network = Network.objects.get(pk=object_id)
    
    # remove relation between the network and selected host(s)
    if request.POST.getlist('remove_host'):
        hosts_pk = request.POST.getlist('remove_host')
        network_host = NetworkHost.objects.filter(network=network, host__pk__in=hosts_pk)
        network_host.delete()
    
    # create relation between the network and selected host
    if request.POST.get('add_host'):
        host = Host.objects.get(pk=request.POST.get('add_host'))
        network_host = NetworkHost(network=network, host=host)
        network_host.save()
    
    queryset = Network.objects.all()
    related_hosts = [nh.host.pk for nh in NetworkHost.objects.filter(network=network)]
    hosts = Host.objects.filter(pk__in=related_hosts)
    if hosts:
        hosts_other = Host.objects.exclude(pk__in=related_hosts)
    else:
        hosts_other = Host.objects.all()
    extra_context = {
        'hosts': hosts,
        'hosts_other': hosts_other
    }
    return object_detail(request, queryset, object_id, extra_context=extra_context)

def network_events(request, object_id):
    """Display events related to network"""
    network = Network.objects.get(pk=object_id)
    queryset = Network.objects.all()
    related_hosts = [nh.host.pk for nh in NetworkHost.objects.filter(network=network)]
    events = Event.objects.filter(source_host__pk__in=related_hosts)
    extra_context = {
        'events': events
    }
    return object_detail(request, queryset, object_id,
                         extra_context=extra_context,
                         template_name='networks/network_events.html')
