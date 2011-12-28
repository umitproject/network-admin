XAuth reference
===============

XAuth is our own implementation of OAuth protocol. It was designed as
an authorization mechanism in web APIs. To understand our idea, take a look
at the following workflow:

#. Getting the Access Token

    #. User gets his Consumer Key and Consumer Secret.
    #. Client application sends Consumer Key, Consumer Secret and user's credentials to get Access Token.

#. Using the Access Token

    #. Client application is provided with an Access Token.
    #. Using an Access Token, client application can access user's private data.

As you probably know, the workflow above is a little bit different than the one
describing the original OAuth. However, the changes we made were necessary to
fit this protocol in this new situation which is web API.

``netadmin.utils.xauth`` module reference
-----------------------------------------

.. exception:: XAuthError

    Raised in case of error related to XAuth protocol

.. exception:: NetadminClientError

    Raised when client was misconfigured

.. class:: NetadminXAuthClient(consumer_key, consumer_secret, api_url)

    Simple XAuth client for working with Network Administrator's API

    .. attribute:: access_token

    .. method:: fetch_access_token(username, password)

        Fetches access token based on user credentials

    .. method:: set_access_token(token)

        Sets access token to specified value

    .. method:: get(resource_url, body='')

        Sends GET request

    .. method:: post(resource_url, body='')

        Sends POST request

    .. method:: get_host_list

        Returns list of hosts

    .. method:: get_host(host_id)

        Returns host with the given ID

    .. method:: get_network_list

        Returns list of networks

    .. method:: get_network(net_id)

        Returns network with the given ID

    .. method:: report_event(description, short_description, timestamp, protocol, event_type, fields_class, hostname='', host_ipv4='', host_ipv6='', *args, **kwargs)

        Reports event

        .. Note:: To send additional fields just pass them as named parameters

Example
-------

Here is a simple example, which was first published on Umit Project's blog [#f1]_::

    from netadmin.utils.xauth import NetadminXAuthClient

    # all these values below should be given by a user
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    USER_NAME = ''
    USER_PASSWORD = ''
    API_URL = 'http://ns-dev.appspot.com'

    if __name__ == '__main__':
        client = NetadminXAuthClient(CONSUMER_KEY, CONSUMER_SECRET, API_URL)

        # you can skip this line if you already have the access token
        access_token = client.fetch_access_token(USER_NAME, USER_PASSWORD)

        client.set_access_token(access_token)

        # at this poing you can get or post any data, e.g.:
        host_list = client.get_host_list()
        for host in host_list["hosts"]:
            id = host["id"]
            host_data = client.get_host(id)
            print host_data["host_name"], host_data["ipv4"]

Once you've created XAuth client, you can also report events to Network Administrator instance::

    import datetime
    import subprocess
    from subprocess import PIPE
    from socket import gethostname

    uptime = subprocess.Popen('/usr/bin/uptime', stdout=PIPE).communicate()[0]

    client.report_event(
        description="Here goes a detailed description",
        short_description="Shortly about an event",
        timestamp=datetime.datetime.now(), protocol="ABCD",
        event_type="INFO", hostname=gethostname(),
        fields_class="CustomEvent", uptime=uptime)

.. rubric:: Footnotes

.. [#f1] http://blog.umitproject.org/2011/09/writing-custom-client-for-network.html
