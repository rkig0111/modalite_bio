#
# This file is part of the BIOM_AID distribution (https://bitbucket.org/kig13/dem/).
# Copyright (c) 2020-2021 Brice Nord, Romuald Kliglich, Alexandre Jaborska, Philomène Mazand.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import annotations
from django.core.checks import Error, register
from django.apps import apps


@register()
def smart_view_checks(app_configs, **kwargs):
    errors = []
    # ... your check logic here
    if app_configs is None:
        app_configs = apps.get_app_configs()

    # print(app_configs, kwargs)
    # Collect Smart classes (SmartViews & SmartPages)
    ...

    # Check SmartViews
    ...

    # Check SmartPages
    ...

    check_failed = False
    checked_object = None

    if check_failed:
        errors.append(
            Error(
                'an error',
                hint='A hint.',
                obj=checked_object,
                id='myapp.E001',
            )
        )
    return errors
