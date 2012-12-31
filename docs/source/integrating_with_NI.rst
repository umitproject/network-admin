Integrating with the Network Inventory
======================================

Network Administrator is a monitoring tool - it can analyze data and present it
to you, but it cannot fetch the data from remote hosts itself. This is why the
Umit Project gives you the Network Inventory - an application that can gather
data from your hosts and send it to the Network Administrator. In fact NI is a
set of applications and you will need two of them: the Agent and the Server.
The Agent lives on every host you want to monitor - it fetches data like uptime
or RAM usage and sends it to the Server, which gathers these notifications and
sends them periodically to the Network Administrator. The following picture
presents a general look at the NI-NA architecture::

    +----------+          +-----------+          +-----------------------+
    |          |   n..1   |           |   n..1   |                       |
    | NI Agent |--------->| NI Server |--------->| Network Administrator |
    |          |          |           |          |                       |
    +----------+          +-----------+          +-----------------------+

This tutorial describes how to set up and run your own Network Inventory.

Installing and running the Server
---------------------------------

Clone the repository::

    $ git clone git://github.com/umitproject/network-inventory.git

Go to ``network-inventory`` directory and run::

    $ python setup.py install_server

You will be prompted for server's credentials and database details::

    Enter the administrator password associated with the username "admin"
    Notifications Server Admin Password:
    Confirm Notifications Server Admin Password:
    Enter Mongo Database host [localhost]:
    Enter Mongo Database port (blank for default):
    Enter Mongo Database Username (blank for none):

Now edit the ``umit_server.conf`` file, go to ``NetworkAdministratorSender``
section and set Network Administrator's options:

    * **username**, **password** -- user account credentials
    * **host** -- host name, eg. *example.com*
    * **notification_queue_size** -- the number of notifications that will be
      queued before sending to the Network Administrator

Finally you can run the Server::

    $ umit_ni_server.py

Installing and running the Agent
--------------------------------

Clone the repository::

    $ git clone git://github.com/umitproject/network-inventory.git

Go to ``network-inventory`` directory and run::

    $ python setup.py install_agent

You will be prompted for details of communication with the server -- set these
options according to the Server's setup::

    Should the data transfer with the Notifications Server be encrypted? [y/N]
    Should the data transfer with the Notifications Server be authenticated? [y/N]
    Enter Notifications Server Address IP:
    Enter Notifications Server listening port [20000]:
    Notifications Server Username:
    Notifications Server Password:
    Confirm Notifications Server Password:

Now that the Agent is already installed, edit ``umit_agent.conf`` file, go to
``DeviceSensor`` section and set ``reporting_enabled`` option to ``True``.

At this point you may run the Agent::

    $ umit_ni_agent.py

Additional notes
----------------

Before reporting a bug, please read the following notes, as they may help to
solve your problem:

    * if having any trouble, the first thing to do is edit configuration files
      (``umit_agent.conf`` and ``umit_server.conf``) and set ``log_level``
      option to ``debug`` -- this way you will be able to see a detailed debug
      information in log files
    * communication between the Network Inventory Server and the Network
      Administrator goes over HTTPS, so remember to set up a SSL engine and
      certificate on you web server (the one serving NA)
    * if you are using NI on Unix-like systems, remember that all above
      commands must be run as a root
