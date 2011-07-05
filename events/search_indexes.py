import search
from search.core import startswith
from events.models import Event

search.register(Event, ('message', ), indexer=startswith)

