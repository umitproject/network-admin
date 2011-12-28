The basic guide for creating a Network Administrator plugin
===========================================================

Here we present you a comprehensive guide to writing plugins for
Network Administrator. Developing these extensions is quite simple, however
there are two requirements you should meet to write them freely:

    * at least basic Python programming skills,
    * basic knowledge of Django template language.
    
If you don't feel confident about your skills, go to Network Administrator
source and look into the ``installed_plugins`` directory, where you will
find code of some plugins that already work. Now let's get to work.
    
Before you start
----------------

On the very beggining, please go to your project's root directory and
find subdirectory called ``installed_plugins``--this is the place where all
plugins live. Don't worry if you can't find it--you can create it any time.
Every package placed there will be recognized as a plugin under one condition:
it has to contain a module called ``main.py``. Any other file which you are going
to use should be placed in this package to maintain the code clean and
well-organized.

After creating a package with main.py inside, simply edit this file.
At first you should create there a subclass of the Plugin (you will find it
in ``netadmin.plugins``). This subclass will be a starting point for all
plugin's features.


Subclassing Plugin class
------------------------

Create a class deriving from the Plugin and define fields ``name``, ``description``
and ``author`` to provide users with more detailed data about your plugin.
Here is a short example::

    from netadmin.plugins import Plugin
    
    class MyPlugin(Plugin):
        name = "my first plugin"
        description = "here goes a description of my plugin"
        author = "Me, <me@email.com>"
        
.. Note::
	Writing a comprehensive docstring would be a great advantage (it is
	possible that in the future these docstrings will be displayed in admin pages).

In fact you can write more than one plugin class. However, if you want a class
to be recognised by Network Administrator, you have to put it on the list
called ``__plugins__``. So lets get back to the example above and define that list:

    __plugins__ = [MyPlugin]

Now, after you created a list with a class object on it, your plugin should be
visible on "Plugins" page, where you can activate it.


Activating and deactivating plugins
-----------------------------------

There are two special methods: ``activate()`` and ``deactivate()`` which you can override
to run some extra code, respectively when plugin is being activated or deactivated.
These methods don't accept any arguments.


Actions
-------

The basic method of extending Network Administrator is defining actions
that will be called in specific places of templates. Almost every action is
connected with an object which can be modified before rendering. If such an
object exists you can change it or event replace it with another one
(the second solution is not recommended).

To define actions, you have to create method called ``actions()`` that have to
return a list of 2-element tuples, where the first element is action's name
and the second one is callback function::

    class MyPlugin(Plugin):
    
        ...
        
        def actions(self):
            return [
                ('host_detail_name', lambda hostname: hostname.upper()),
                ('event_detail_event_type', self.display_event_type)
            ]
            
        def display_event_type(self, event_type):
            return "%s (alert level %i)" % \
                (event_type.name, event_type.alert_level)
        
The best way to find an action you are looking for is to look into the Network
Administrator templates--the string placed next to ``{% action %}`` tag is action's
name.


Custom options
--------------

Custom options is a simple mechanism that lets you store additional
data for your plugins and widgets. It is based on a set of functions for
getting and setting options, so you don't have to touch the database directly.
You will find all available functions in ``netadmin.plugins.options`` module and
below we present only the most important of them.

.. function:: set_option (name, value, user=None)

    Sets value of an option. If option with given name does not exists, it is
    created.
    
.. function:: get_option (name, default, user=None)

    Returns value of an option. If option with given name does not exists, it is
    created and its value is set to default.
    
It is possible to set option only for a single user--you just have to pass
User instance as a third parameter. When you set option without
passing user object, we call it "global option". Here is a short example:

    >>> host = get_host(id)
    >>> # Accessing option that doesn't exist
    ... a = get_option('A', default='not found', user=host.user)
    >>> print a # option has been created and set to default
    not found
    >>> # Now let's set another option called 'B' and get its value
    >>> set_option('B', 'here goes value', user=host.user)
    >>> b = get_option('B', default='not found', user=host.user)
    >>> print b # option already exists so default value was ignored
    here goes value
    >>> # what happens when we try to access option 'B' without passing a user:
    ... b = get_option('B', default='not found')
    >>> print b
    not found
    >>> # Setting a global option
    ... set_option('C', 123)
    >>> # what happens when we try to access global option 'C' with given user instance:
    ... c = get_option('C', default='not found', user=host.user)
    >>> print c # option 'C' doesn't exist for specified user
    not found
    
.. Note::
	In fact every option is stored as a string--its value is converted to string
	using ``str()`` function. Therefore, what you get using ``get_option()`` method is always
	a string.


Note on naming
--------------

Generally there are no restrictions in naming custom options. However, we strongly
recommend the following scheme:

    <plugin_or_widget_name>_<option_name>
    
where both names are written in lowercase and words are separated with a single
underscore. This simple convention prevents the use of the same option name by
different plugins.

    
Plugin settings page
--------------------

The best plugin is the one that is highly flexible. Therefore you may want to
create a settings page for your plugin. You do this by overriding options()
method. It should return a dictionary where every key-value pair describes
one option and its parameters. Look at the example below::

    class MyPlugin(Plugin):
        ...
    
        def options(self):
            return {
                'my_plugin_email': {
                    'label': 'Your e-mail address',
                    'type': 'string',
                    'default': ''
                },
                'my_plugin_notify': {
                    'label': 'Send notifications every',
                    'choices': [(1, 'Day'), (7, 'Week')]
                }
            }

Here is the list of available parameters with which you can describe option:

    * label -- a label representing the option
    * type -- a string defining type of option, default: ``string``;
      this parameter is omitted if you provide a ``choices`` value
    * choices (optional) -- list of choices for this option in
      a Django-style format (https://docs.djangoproject.com/en/dev/ref/models/fields/#field-choices)
    * default (optional) -- default value for this option
    * return_func (optional)-- a function that will be used to convert option's stored value
      from string to any other object; this function have to accept only one
      argument which is a value fetched from database 

You can choose option's type from the list below:

    * string (default) -- a string, represented by text input
    * integer -- an integer number, represented by text input
    * bool -- a boolean value, represented by ``True``-``False`` select box


Accessing options inside plugin
-------------------------------

The other way you can access defined options is using ``get_option()`` method.
The only thing that differs this method from ``get_option()`` function is that
the method uses ``return_func`` parameter to convert stored value.
This short example should explain everything::

    class MyPlugin(Plugin):
        ...
        
        def options(self):
            return {
                'my_plugin_age': {
                    'label': 'Your age',
                    'type': 'integer',
                    'default': '123',
                    'return_func': lambda value: int(value)
                }
            }
            
    >>> set_option('my_plugin_age', 123)
    >>> plugin = MyPlugin()
    >>> plugin.get_option('my_plugin_age')
    123
    >>> get_option('my_plugin_age', '')
    '123'


Widgets
-------

Developing widgets is pretty like writing plugins. You should start with
writing a class deriving from Widget. It have to override the following
fields: ``name``, ``description`` and ``template_name``. The first one is a name
for your widget, the second is a description and it depends on you what
user will find there, the last is a name of template file which will be used
to render the widget.

The second step is writing ``get_title()`` method. It should return string that
will be displayed on widget's title bar.

Finally, you have to override the ``context()`` method. It accepts one argument
called ``widget`` which is an instance of widget settings object. You can use
this object, for example, to access user who owns the widget (for more
details see: ``netadmin.plugins.models.WidgetSettings`` documentation). The method
should return a dictionary with context variables. You will be able to use
these variables in widget template. Here is a short example::

    class MyWidget(Widget):
        name = "My first widget"
        description = "This is my first widget"
        
        template_name = "my_widget.html"
        
        def get_title(self):
            return "Host list"
            
        def context(self, widget):
            user = widget.widgets_area.user
            hosts = get_hosts(user=user)
            return {
                'hosts': hosts[:5]
            }


Writing widget template
-----------------------

After you created widget class, it's time to write a template. Everything you
should know about creating templates was written on this page:

https://docs.djangoproject.com/en/dev/topics/templates/

In your template you can use context variables returned by ``context()`` method
and request object passed from a template in which the widget is being rendered.
This is how template ``my_widget.html`` might look like::

    <h3>{{ request.user.username }}'s hosts</h3>
    <ul>
    {% for host in hosts %}
        <li>{{ host.name }}, {{ host.ipv4 }}, {{ host.ipv6 }}
    {% endfor %}
    <ul>


Widgets and options
-------------------

Both ``options()`` and ``get_option()`` methods works the same way like in plugins.
The only difference is additional argument ``widget`` which is described above.


Shortcut functions
------------------

You probably noticed that we used in this tutorial several functions like
``get_host()`` or ``get_hosts()``. These are so called 'shortcut functions'. They
were created so you don't have to code or even know how to perform database
queries. There is a whole set of useful functions for getting hosts, networks,
events etc. To read more about shortcuts see documentation of :doc:`shortcuts`.

.. Note::
	Shortcut functions were made also for backward compatibility, so you
	don't have to change your plugins every time we update the core of NA.


Summary
-------

If you're looking for more information about how Network Administrator works
or how good plugin should be written, see NA's source and documentation.
You may also contact with the author or Umit Project team.
