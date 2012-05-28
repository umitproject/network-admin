Installation instructions
=========================

Before running the Network Administrator, you have to install the following
software:

* Python 2.7 (you may start here: http://python.org/getit/)
* pip (http://pypi.python.org/pypi/pip)

If you are using Linux, you will probably find both of these packages in
official repositories. For example, in Debian Wheezy distribution, just run
the following command::

    sudo apt-get install python2.7 python-pip

Now, when you have both Python and pip, you can setup NA for development or
deploy it on a production server. The next section describes the most common
scenarios of installation.

Installation options
--------------------

Depending on your needs, you may want to set up NA in a different way. In this
section you will find several tutorials covering the most common scenarios:

#. Install NA for development
#. Deploy NA on Debian with Apache and mod_wsgi
#. Deploy on the Google AppEngine

Install NA for development
""""""""""""""""""""""""""

If you want to support development of the Network Administrator, this is the
place where you should start.

First, you have to clone NA's Git repository::

    git clone -b develop git://github.com/umitproject/network-admin.git

Even after installing packages mentioned in the previous section, NA still has
some dependencies. To get them just run this command::

    pip install -r dependencies.txt

Now you have to set up a database connection. In this tutorial we will use
SQLite3 [#sqlite]_, but you can use any other database like MySQL, PostgreSQL
or Oracle. To use SQLite as a database backend just create file
``local_settings.py`` in project's root directory and put there the following
code::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'netadmin.db',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }

Next, you have to synchronise your database::

    python manage.py syncdb

To make sure that everything will run correctly on you system, run tests::

    python manage.py test events networks reportmeta webapi

At this point everything is ready to run the development server::

    python manage.py runserver

That's it! Now open a web browser and go to address: ``127.0.0.1:8000``.

Deploy NA on Debian with Apache and mod_wsgi
""""""""""""""""""""""""""""""""""""""""""""

Deployment on Apache is the best way to use NA in production on your own
machine.

#. Install Apache and mod_wsgi::

    apt-get install apache2 libapache2-mod-wsgi

#. Clone NA's Git repository::

    git clone -b develop git://github.com/umitproject/network-admin.git

#. Move all files from NA's root directory to the directory accessible
   by Apache, e.g. ``/var/www/netadmin/``. From now on we will be calling this
   directory *the application's directory*.

#. Go to the application's directory and install dependencies::

    pip install -r dependencies.txt

#. To set up connection with SQLite [#sqlite]_ database, create file
   ``local_settings.py`` in application's directory and put there the following
   code::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/var/www/netadmin/netadmin.db',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }

#. Open ``settings.py`` file and change this line::

    DEBUG = True

   to::

    DEBUG = False

#. Put the following code into the file ``handler.wsgi`` in application's
   directory::

    import os
    import sys

    sys.path.append('/var/www/netadmin')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    import django.core.handlers.wsgi

    application = django.core.handlers.wsgi.WSGIHandler()

#. Go to ``/etc/apache2/sites-available/``, create file ``netadmin`` and edit
   it::

    <VirtualHost *:80>
        ServerName  www.example.com
        DocumentRoot /var/www/netadmin

        WSGIDaemonProcess www-data processes=2 maximum-requests=500 threads=1
        WSGIProcessGroup www-data
        WSGIScriptAlias / /var/www/netadmin/handler.wsgi

        Alias /static/ /var/www/netadmin/static/
        <Directory /var/www/netadmin/static>
            Options -Indexes
        </Directory>
    </VirtualHost>

   Before saving the file remember to replace ``www.example.com`` with your
   own server name. If you want to work on server's security or performance,
   don't hesitate to change this configuration, as this is just the example of
   how you may set it up. For more details about available options, please
   refer to the documentation of Apache [#apache]_.

#. Synchronise the database::

    python manage.py syncdb

#. Finally, restart Apache web server::

    service apache2 restart

Deploy on the Google AppEngine
""""""""""""""""""""""""""""""

Network Administrator perfectly integrates with the Google AppEngine, so it's
the best choice if you want to deploy NA in the cloud.

However, to deploy application on the GAE, you have to set it up locally as
well.

#. Download and install the Google AppEngine SDK for Python [#gae]_. Please
   refer to the GAE documentation for details.

#. Create a new directory for you project.

#. Clone NA's Git repository::

    git clone -b develop git://github.com/umitproject/network-admin.git

#. Move all files from cloned repository to the project's directory.

#. Download the following packages and place them in the project's directory:

   * django
   * django-piston
   * geraldo
   * djangotoolbox
   * django-dbindexer
   * django-nonrel [#djangononrel]_
   * djangoappengine [#djangoappengine]_
   * django-autoload [#djangoautoload]_
   * django-permission-backend-nonrel [#permissionbackend]_
   * nonrel-search [#nonrelsearch]_

   All packages except the last five are available at PyPI, so you can get
   them using ``pip install``. The others have to be downloaded manually.

   .. Note:: Google AppEngine provides only Python's standard library, so any
      other package you want to use have to be uploaded along with
      application's source code.

#. Open the file ``settings.py`` and uncomment all lines preceded by comments
   like this one::

    # uncomment the next line if you want to run NA on the Google AppEngine

#. In the same file set ``SITE_DOMAIN`` variable to the domain of your GAE
   application::

    SITE_DOMAIN = 'example.appspot.com'

#. Still in the same file change this line::

    DEBUG = True

   to::

    DEBUG = False

#. Create file ``app.yaml`` and put there the following code::

    application: example
    version: 1
    runtime: python
    api_version: 1

    builtins:
    - remote_api: on
    - datastore_admin: on

    inbound_services:
    - warmup

    handlers:
    - url: /_ah/queue/deferred
      script: djangoappengine/deferred/handler.py
      login: admin

    - url: /media/admin
      static_dir: django/contrib/admin/media
      expiration: '0'

    - url: /notifications/send_all/
      script: djangoappengine/main/main.py
      secure: always
      login: admin

    - url: /user/remove_inactive_users/
      script: djangoappengine/main/main.py
      secure: always
      login: admin

    - url: /.*
      script: djangoappengine/main/main.py

   Remember to replace ``example`` with your application's name.

#. Synchronise the database::

    python manage.py syncdb

#. Now the application is ready for deployment, just run the following
   command::

    python manage.py deploy

Scheduling maintenance tasks
----------------------------

There are some tasks that Network Administrator needs to run periodically, for
example dispatching notifications. To run these jobs you have to use an external
scheduler like cron. Check all the commands below and make sure that they run
often enough, otherwise NA will not work properly.

.. Note::
    If you are deploying NA on the Google AppEngine, you don't have to use any
    external scheduler. Just use the ``app.yaml`` file listed above and GAE
    will know what to do.

Removing inactive accounts
""""""""""""""""""""""""""

Upon registering in NA, user has 7 days to activate account. After that, account
should be deleted. The following command removes all inactive accounts which are
older than 7 days::

    python manage.py remove_inactive_users

Dispatching notifications
"""""""""""""""""""""""""

Instead of sending notifications immediately, NA groups them by email address
and leaves them for dispatcher to send them later on. This mechanism prevents
NA from spamming your email box. The command below calls dispatcher to send
grouped notifications::

    python manage.py send_notifications


Final notes
-----------

If you find this tutorial incomplete or buggy, please report to the Umit Project
development team: http://dev.umitproject.org. We will be grateful for any comments and suggestions.


.. rubric:: Footnotes

.. [#sqlite] Running NA with SQLite requires installing both SQLite3 and
   ``pysqlite`` package.
.. [#apache] http://httpd.apache.org/docs/2.0/
.. [#gae] http://code.google.com/intl/pl/appengine/downloads.html#Google_App_Engine_SDK_for_Python
.. [#djangononrel] http://bitbucket.org/wkornewald/django-nonrel/get/tip.zip
.. [#djangoappengine] http://bitbucket.org/wkornewald/djangoappengine/get/tip.zip
.. [#djangoautoload] http://bitbucket.org/twanschik/django-autoload/get/tip.zip
.. [#permissionbackend] https://github.com/django-nonrel/django-permission-backend-nonrel
.. [#nonrelsearch] https://bitbucket.org/twanschik/nonrel-search/src
