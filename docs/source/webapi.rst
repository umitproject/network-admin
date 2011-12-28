Web API reference
=================

Network Administrator's web API's main
purpose is to receive notifications and give access to hosts, networks
and reports data. It is based on RESTful web services and uses JSON to
serialize data.

The API has its private and public sections. The private section's task
is to receive notifications (events) from servers and save them into the
database. The public part is supposed to be the interface that will give
external applications access to informations about hosts, networks and
reports.

Our next goal for this API is to provide authentication with OAuth.
So far we are using system which simply sends user login and password
encoded with the base64 library.

Host handler
------------

Host handler is a part of the public API. It gives access to hosts data.

GET
^^^

Returns host details if host_id is specified, otherwise returns
list of hosts.


Request parameters:
	* host_id (optional) - if specified, host details are returned
	* order_by (optional) - if host_id is not specified, order hosts list according to this parameter; allowed values are:

		* name - order by name
		* last_event - order by occurance of last event

	* limit - maximum number of hosts on a list

Host details response:
	* host_id
	* host_name
	* host_description
	* ipv4 - IPv4 address of the host
	* ipv6 - IPv6 address of the host
	* events (optional) - list of events for the host

		* id - event identifier
		* message - event message

Hosts list response:
	* hosts

		* id - host identifier
		* name - host name

Network handler
---------------

This handler gives access to all informations about networks, like
networks list or details of the specified network. This is a part
of the public API.

GET
^^^

If the network_id is specified returns network details,
otherwise returns networks list.

Request parematers:
	* network_id (optional) - network which details we want
	* get_hosts (optional) - if 'true' and network_id is specified, then list of hosts in the network is returned
	* order_by (optional) - if network_id is not specified then networks list will be sorted according to this parameter; the allowed values are:

		* name - order by name
		* last_event - order by occurance of last event

Network details response:
	* network_id
	* network_name - name of the network
	* network_description - description of the network
	* hosts (optional)
	
		* id - host identifier
		* name - host name

Networks list reponse:
	* networks
	
		* id - network identifier
		* name - network name

Event handler
-------------

Event handler is responsible for receiving notifications (events)
and saving them to the Network Administrator database. Its second
task is to return events list or details of event.

Every event has its source host which is the host from where it
comes. In the notification the source host is identified by pair
of IPv4 and IPv6 addresses, where the second one is optional so far.
So to relate the upcoming event with the corresponding host in
database we have to search for the host which has the same
addresses like the source host in the notification. 

POST
^^^^

Receives one or more notifications and saves them to the database.
This method is a part of private API.

Case 1: Reporting single event (notification)
"""""""""""""""""""""""""""""""""""""""""""""

Request parameters:
	* description - message describing the event
	* short_description - shorter message, e.g. to use in list
	* timestamp - when the event occurred
	* event_type - type of the event which should also describe its importance
	* protocol - network protocol related to the event
	* hostname - name of the source host
	* source_host_ipv4, source_host_ipv6 - IPv4 and IPv6 addresses of the source host
	* fields_class - monitoring module identifier

Any additional data provided with the event will be serialized and
saved together with fields described above.

Response:
	* status - **ok** or **error**
	* message - details of the result

Case 2: Reporting multiple events at once
"""""""""""""""""""""""""""""""""""""""""

Request parameters:
	* events - list of events serialized with JSON

Response:
	* status - **ok** or **error**
	* message - details of the result

GET
^^^

The part of the public API. If the event_id parameter is specified,
returns event details, otherwise returns events list ordered by timestamp.
In the second case, events may be filtered by source host or
timestamp and their number may be limited. 

Request parameters:
    * source_host - identifier of a source host
    * time_from - include only those events which timestamp is greater or equal than this value
    * time_to - include only those events which timestamp if less than this value
    * limit - maximal number of events on a list

Response for events list:
	* events - list of events
	
		* id - event identifier
		* message - event message

Response for event details:
    * event_id
    * description - event message
    * description - event short message
    * timestamp - event timestamp
    * event_type - type of event 
    * source_host_id - identifier of source host
    * module_id - identifier of monitoring module
    * module_fields - fields defined by monitoring module
