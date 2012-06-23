Models reference
================

``netadmin.events`` --- Events
------------------------------

.. class:: EventType

    Describes type of an event, e.g. INFO, CRITICAL etc. Note that every event
    type is linked with user - its owner. That is because events types are
    created automatically, when events are reported so every user may have
    different set of types.

    Alert level has no effect on reporting events or managing them. This field
    only indicates importance of events and is used to distinguish those of
    them which should be treated differently.

    .. attribute:: name

        human-readable name for event type

    .. attribute:: name_slug

        string identifier used in URLs

    .. attribute:: user

        owner of event type

    .. attribute:: alert_level

        number indicating importance of a type

    .. attribute:: notify

        if ``True``, user will be notified about new events of this type

.. class:: Event

    Event model class represents single notification reported to the Network
    Administrator. The following fields are defined:

    .. attribute:: message

        description of an event

    .. attribute:: short_message

        shorter description (could be used as a title)

    .. attribute:: message_slug

        slug made of ``short_message``

    .. attribute:: timestamp

        moment when event occurred on host

    .. attribute:: protocol

        network protocol

    .. attribute:: event_type

        foreign key to the EventType object which simply stores
        short and readable event name like ``INFO`` or ``WARNING``

    .. attribute:: source_host

        foreign key to the Host object; this is the host from
        where the event came

    .. attribute:: fields_class

        identifier of the class of additional fields

    .. attribute:: fields_data

        serialized fields that contain more specific data
        about the event

    .. attribute:: checked

        ``True`` means that event has been marked by user as known
        (actually this field is important only for alerts, where information
        about event status is really important)

    .. Note::
        Although event hasn't ``user`` field specified, we can say that
        event belongs to the user who owns the source host.

``netadmin.networks`` --- Hosts and networks
--------------------------------------------

.. class:: NetworkObject()

    Abstract model class for objects like host or network.
    Every object belongs to specified user.

    .. attribute:: name

    .. attribute:: description
    
    .. attribute:: user

.. class:: Host()

    A single host in network

    .. attribute:: ipv4

        IPv4 address
        
    .. attribute:: ipv6

        IPv6 address

.. class:: Network()

    Represents a single network


.. class:: NetworkHost()

    Since one cannot use ManyToManyField type in GAE [1], we have to
    write extra model that will provide application with many-to-many
    relationship between networks and hosts.

    To ensure that after deleting host or network its relations will
    be removed too, we have to override delete() method for both
    Host and Network classes. Those methods should look like that::

        def delete(self, *args, **kwargs):
            related = self.networkhost_set.all()
            related.delete()
            super(Network, self).delete(*args, **kwargs)

    for Network class, and::

        def delete(self, *args, **kwargs):
            related = self.networkhost_set.all()
            related.delete()
            super(Host, self).delete(*args, **kwargs)

    for Host class.

    [1] http://www.allbuttonspressed.com/projects/djangoappengine

    .. attribute:: network
    
    .. attribute:: host

``netadmin.reportmeta`` --- Reports
-----------------------------------

.. class:: ReportMeta

    Report Meta class contains all report metadata like its name,
    description, time period and reported object.

    .. attribute:: name

    .. attribute:: description

    .. attribute:: report_period

        Integer value representing period described in report.
        The ``netadmin.reportmeta.models`` module defines all possible values for this field::

            DAILY = 0
            WEEKLY = 1
            MONTHLY = 2

            REPORT_PERIOD = (
                (DAILY, _("Daily")),
                (WEEKLY, _("Weekly")),
                (MONTHLY, _("Monthly"))
            )
            
    .. attribute:: object_type

    .. attribute:: object_id

    .. attribute:: reported_object

    .. attribute:: user

        User who created the report

.. class:: ReportMetaEventType

    Many-to-many relationship between report meta objects
    and event types included in the reports

    .. attribute:: report_meta

    .. attribute:: event_type

``netadmin.users`` -- Users
---------------------------

.. class:: UserProfile

    Extension for standard User model, providing detailed profile

    .. attribute:: user

        Actual user object

    .. attribute:: in_search

        If ``True`` user's profile will be shown in search results

    .. attribute:: is_public

        If ``True`` user's profile page will be available to see for other users
