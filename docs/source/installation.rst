Installation instructions
=========================

To install and run Network Administrator locally, just follow the
instructions below (I assume that you have already installed Python):

#. Clone Git repository::
	
	git clone git://dev.umitproject.org/network-admin.git
	
#. Test main NA's apps::
	
	cd netadmin
	python ../manage.py test events networks reportmeta webapi
	
#. Run Django's development server::
	
	python manage.py runserver
	
#. Open your favourite web browser and check address localhost:8000.
	
Known issues
------------

**Geraldo, Reportlab and zipimport**

Actually this issue doesn't cause problems anymore. Now we are waiting for
response from Geraldo developers.

For more details go here: https://github.com/marinho/geraldo/issues/4

**Nonrel-search and strange issues with creating indexes for models**

After the project growed bigger, the problem with Nonrel-search appeared.
While creating apps which models that uses foreign keys to other apps, you may
see Nonrel-search crashing (search_index fields are not created, thus
searching may not be done). This is probably caused by too complicated imports
relationships. So how it works in NA? In events app there are commented lines
that register models in Django's admin. I have no idea why it works like that,
so I will investigate this issue some day.
