Shortcut functions
==================

The following functions were designed as a layer between plugins and core API.
Using them you don't have to know what's going on "behind the scenes"--with
a single function call you get or manipulate any data you want.

Getting data
------------

.. function:: get_events(time_from=None, time_to=None, source_hosts=[], event_types=[])

    Returns events, optionally filtering them by timestamp
    or source hosts.

.. function:: get_eventtypes(user=None, alert=0)

    Returns events' types, filtering them by user and/or alert
    level if specified.

.. function:: get_user_events(user)

    Returns events reported to the specified user

.. function:: get_alerts(user=None)

    Returns events which type was marked as alert

.. function:: get_host(id)

    Returns host with the given ID

.. function:: get_hosts(user=None)

    Returns hosts owned by the given user

.. function:: get_network(id)

    Returns network with the given ID

.. function:: get_networks(user=None)

    Returns networks owned by the given user