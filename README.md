# Network Administrator


## Table Of Contents

1. License note
2. Installation instructions
3. Known issues


### 1. License Note

Copyright (C) 2011 Adriano Monteiro Marques

Author: Piotrek Wasilewski <wasilewski.piotrek@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

### 2. Installation instructions

To install and run Network Administrator locally, just follow the
instructions below (I assume that you have already installed Python):

1. Clone Git repository: 
    ```
    git clone git://github.com/umitproject/network-admin.git
    ```
    
2. Test main NA's apps:
	```
	cd netadmin
	python ../manage.py test events networks reportmeta webapi
	```

3. Run Django's development server:	
    ```
    python manage.py runserver
    ```
	
4. Open your favourite web browser and check address [http://localhost:8000](http://localhost:8000).
	
### 3. Known issues

#### 3.1 Geraldo, Reportlab and zipimport

Actually this issue doesn't cause problems anymore. Now we are waiting for
response from Geraldo developers.

For more details go [here](https://github.com/marinho/geraldo/issues/4)

#### 3.2 Nonrel-search and strange issues with creating indexes for models

After the project growed bigger, the problem with Nonrel-search appeared.
While creating apps which models that uses foreign keys to other apps, you may
see Nonrel-search crashing (search_index fields are not created, thus
searching may not be done). This is probably caused by too complicated imports
relationships. So how it works in NA? In events app there are commented lines
that register models in Django's admin. I have no idea why it works like that,
so I will investigate this issue some day.