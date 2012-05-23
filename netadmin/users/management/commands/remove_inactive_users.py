#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Adriano Monteiro Marques
#
# Author: Piotrek Wasilewski <wasilewski.piotrek@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _

from netadmin.users.models import UserActivationCode


class Command(NoArgsCommand):

    help = _(u"Removes accounts of inactive users")

    def handle_noargs(self, **options):

        self.stdout.write(_(u"Removing inactive users... "))
        self.stdout.flush()

        codes = UserActivationCode.objects.all()
        for code in codes:
            if not code.is_active():
                code.user.delete()
                code.delete()

        self.stdout.write(_(u"done.\n"))
