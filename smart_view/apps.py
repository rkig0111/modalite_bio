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
from django.apps import AppConfig


class SmartViewConfig(AppConfig):
    name = "smart_view"

    def __init__(self, *args, **kwargs):
        self.smart_format_registry = {}
        super().__init__(*args, **kwargs)

    def ready(self):
        import smart_view.checks  # NOQA

    def register_formats(self, formats: dict):
        self.smart_format_registry.update(formats)
