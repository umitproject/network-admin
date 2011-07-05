import search
from search.core import startswith
from networks.models import Host, Network

search.register(Host, ('name', 'description', 'ipv4', 'ipv6'),
                indexer=startswith)

search.register(Network, ('name', 'description'),
                indexer=startswith)